// Baileys' custom auth-state interface over the Python supervisor's Dict proxy.
//
// WHY BATCHED AND PRELOADED (found live, 2026-11-11): the first version made one HTTP+Dict round
// trip per key. Pairing commits ~800 pre-keys in one transaction, which blew Baileys' timeouts
// ("failed to commit mutations", "Pre-key upload timeout", "transaction failed, rolling back").
// Now the whole state is read ONCE at start (so every later read is a cache hit, and an absent
// key is genuinely absent), and each commit is ONE write call. Every change is still awaited into
// the Dict before Baileys continues, so the stored state is never behind the live session.
import { initAuthCreds, BufferJSON, proto } from "@whiskeysockets/baileys";

export function makeKv(base, token) {
  const call = async (route, body) => {
    const r = await fetch(base + route, { method: "POST", headers: { "x-ctl": token, "content-type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error("kv " + route + " " + r.status);
    return r.json();
  };
  return {
    all: async () => (await call("/kv/all", {})).items || {},
    setMany: (items) => call("/kv/setmany", { items }),
    delMany: (keys) => call("/kv/delmany", { keys }),
    clear: () => call("/kv/clear", {}),
  };
}

export async function useKvAuthState(kv) {
  const cache = new Map(Object.entries(await kv.all()));      // key -> JSON string, as stored
  const parse = (k) => (cache.has(k) ? JSON.parse(cache.get(k), BufferJSON.reviver) : null);
  const creds = parse("creds") || initAuthCreds();
  const commit = async (sets, dels) => {
    if (Object.keys(sets).length) await kv.setMany(sets);
    if (dels.length) await kv.delMany(dels);
    for (const [k, v] of Object.entries(sets)) cache.set(k, v);   // cache follows only a durable write
    for (const k of dels) cache.delete(k);
  };
  return {
    state: { creds, keys: {
      get: async (type, ids) => {
        const out = {};
        for (const id of ids) {
          let v = parse(`${type}-${id}`);
          if (type === "app-state-sync-key" && v) v = proto.Message.AppStateSyncKeyData.fromObject(v);
          out[id] = v;
        }
        return out;
      },
      set: async (data) => {
        const sets = {}, dels = [];
        for (const type of Object.keys(data)) for (const id of Object.keys(data[type])) {
          const v = data[type][id], k = `${type}-${id}`;
          if (v == null) dels.push(k); else sets[k] = JSON.stringify(v, BufferJSON.replacer);
        }
        await commit(sets, dels);
      } } },
    saveCreds: () => commit({ creds: JSON.stringify(creds, BufferJSON.replacer) }, []),
    _cache: cache,
  };
}
