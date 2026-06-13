const axios = require('axios');

exports.handler = async function(context, event, callback) {
  const twiml = new Twilio.twiml.MessagingResponse();

  const userMessage = (event.Body || '').trim();
  const from        = event.From || '';

  console.log(`[chike] Message from ${from.slice(0,8)}***: ${userMessage.slice(0,80)}`);

  // Greeting triggers — return welcome without calling Cerebrium
  const GREETINGS = new Set([
    'habari','hujambo','mambo','hello','hi','hey',
    'salaam','salam','start','help','msaada','chike','karibu',
  ]);

  if (GREETINGS.has(userMessage.toLowerCase())) {
    twiml.message(
      'Habari! Mimi ni *Chike* kutoka *Africa Giants*.\n\n' +
      '_Fahamu Biashara Yako, Maarifa Yako._\n\n' +
      'Ninakusaidia na maswali ya biashara Tanzania:\n' +
      '• Kodi (VAT, PAYE, SDL, WHT)\n' +
      '• Usajili (BRELA, TRA, NSSF, OSHA, WCF)\n' +
      '• Sheria za biashara (GN 487A, vibali)\n' +
      '• Mahitaji ya kufuata sheria\n\n' +
      'Uliza swali lolote. Ninajibu kwa Kiswahili na Kiingereza.\n\n' +
      '---\n\n' +
      'Hi! I am *Chike* from *Africa Giants*.\n\n' +
      '_Understand Your Business, That Knowledge Is Yours._\n\n' +
      'Ask me anything about Tanzanian business, tax, or compliance.'
    );
    return callback(null, twiml);
  }

  // Call Cerebrium
  try {
    const response = await axios.post(
      `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run`,
      { message: userMessage },
      {
        headers: {
          'Authorization': `Bearer ${context.CEREBRIUM_API_KEY}`,
          'Content-Type': 'application/json',
        },
        timeout: 90000,
      }
    );

    const reply = response.data?.result?.reply || '';

    if (!reply) {
      twiml.message(
        'Samahani, Chike hakupata jibu. Jaribu tena.\n\n' +
        'Sorry, Chike did not get a reply. Please try again.'
      );
    } else {
      twiml.message(reply);
    }

  } catch (error) {
    console.error('[chike] Cerebrium error:', error.message);
    twiml.message(
      'Samahani, Chike hakuweza kukusaidia sasa hivi. ' +
      'Tafadhali jaribu tena baadaye.\n\n' +
      'Sorry, Chike could not help right now. ' +
      'Please try again shortly.'
    );
  }

  return callback(null, twiml);
};
