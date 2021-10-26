try {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();
} catch (e) {
    console.error(e);
    $('.no-browser-support').show();
    $('.app').hide();
}

recognition.lang = 'en';
var noteTextarea = $('#note-textarea');
var instructions = $('#recording-instructions');

var noteContent = '';

/*-----------------------------
      Voice Recognition
------------------------------*/

// If false, the recording will stop after a few seconds of silence.
// When true, the silence period is longer (about 15 seconds),
// allowing us to keep recording even when the user pauses.
recognition.continuous = true;

// This block is called every time the Speech APi captures a line.
recognition.onresult = function(event) {

    // event is a SpeechRecognitionEvent object.
    // It holds all the lines we have captured so far.
    // We only need the current one.
    var current = event.resultIndex;

    // Get a transcript of what was said.
    var transcript = event.results[current][0].transcript;

    // Add the current transcript to the contents of our Note.
    // There is a weird bug on mobile, where everything is repeated twice.
    // There is no official solution so far so we have to handle an edge case.
    var mobileRepeatBug = (current == 1 && transcript == event.results[0][0].transcript);

    if (!mobileRepeatBug) {
        noteContent += transcript;
        noteTextarea.val(noteContent);
    }
};

recognition.onstart = function() {
    instructions.text('Voice recognition activated. Try speaking into the microphone.');
}

recognition.onspeechend = function() {
    instructions.text('You were quiet for a while so voice recognition turned itself off.');
}

recognition.onerror = function(event) {
    if (event.error == 'no-speech') {
        instructions.text('No speech was detected. Try again.');
    };
}



/*-----------------------------
      App buttons and input
------------------------------*/

function start(event) {
    if (noteContent.length) {
        noteContent += ' ';
    }
    recognition.start();
    instructions.text('Voice recognition started.');
}

function stop() {
    recognition.stop();
    instructions.text('Voice recognition paused.');
}


function set_lang_code() {
    lang_name = document.getElementById('lang_name').value;
    document.getElementById('lang_name2').value = lang_name;
    let lang = ['Afar', 'Abkhazian', 'Avestan', 'Afrikaans', 'Akan', 'Amharic', 'Aragonese', 'Arabic', 'Assamese', 'Avaric', 'Aymara', 'Azerbaijani', 'Bashkir', 'Belarusian', 'Bulgarian', 'Bihari languages', 'Bislama', 'Bambara', 'Bengali', 'Tibetan', 'Breton', 'Bosnian', 'Catalan; Valencian', 'Chechen', 'Chamorro', 'Corsican', 'Cree', 'Czech', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic', 'Chuvash', 'Welsh', 'Danish', 'German', 'Divehi; Dhivehi; Maldivian', 'Dzongkha', 'Ewe', 'Greek, Modern (1453-)', 'English', 'Esperanto', 'Spanish', 'Estonian', 'Basque', 'Persian', 'Fulah', 'Finnish', 'Fijian', 'Faroese', 'French', 'Western Frisian', 'Irish', 'Gaelic; Scottish Gaelic', 'Galician', 'Guarani', 'Gujarati', 'Manx', 'Hausa', 'Hebrew', 'Hindi', 'Hiri Motu', 'Croatian', 'Haitian; Haitian Creole', 'Hungarian', 'Armenian', 'Herero', 'Interlingua (International Auxiliary Language Association)', 'Indonesian', 'Interlingue; Occidental', 'Igbo', 'Sichuan Yi; Nuosu', 'Inupiaq', 'Ido', 'Icelandic', 'Italian', 'Inuktitut', 'Japanese', 'Javanese', 'Georgian', 'Kongo', 'Kikuyu; Gikuyu', 'Kuanyama; Kwanyama', 'Kazakh', 'Kalaallisut; Greenlandic', 'Central Khmer', 'Kannada', 'Korean', 'Kanuri', 'Kashmiri', 'Kurdish', 'Komi', 'Cornish', 'Kirghiz; Kyrgyz', 'Latin', 'Luxembourgish; Letzeburgesch', 'Ganda', 'Limburgan; Limburger; Limburgish', 'Lingala', 'Lao', 'Lithuanian', 'Luba-Katanga', 'Latvian', 'Malagasy', 'Marshallese', 'Maori', 'Macedonian', 'Malayalam', 'Mongolian', 'Marathi', 'Malay', 'Maltese', 'Burmese', 'Nauru', 'Bokmål, Norwegian; Norwegian Bokmål', 'Ndebele, North; North Ndebele', 'Nepali', 'Ndonga', 'Dutch; Flemish', 'Norwegian Nynorsk; Nynorsk, Norwegian', 'Norwegian', 'Ndebele, South; South Ndebele', 'Navajo; Navaho', 'Chichewa; Chewa; Nyanja', 'Occitan (post 1500)', 'Ojibwa', 'Oromo', 'Oriya', 'Ossetian; Ossetic', 'Panjabi; Punjabi', 'Pali', 'Polish', 'Pushto; Pashto', 'Portuguese', 'Quechua', 'Romansh', 'Rundi', 'Romanian; Moldavian; Moldovan', 'Russian', 'Kinyarwanda', 'Sanskrit', 'Sardinian', 'Sindhi', 'Northern Sami', 'Sango', 'Sinhala; Sinhalese', 'Slovak', 'Slovenian', 'Samoan', 'Shona', 'Somali', 'Albanian', 'Serbian', 'Swati', 'Sotho, Southern', 'Sundanese', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Tajik', 'Thai', 'Tigrinya', 'Turkmen', 'Tagalog', 'Tswana', 'Tonga (Tonga Islands)', 'Turkish', 'Tsonga', 'Tatar', 'Twi', 'Tahitian', 'Uighur; Uyghur', 'Ukrainian', 'Urdu', 'Uzbek', 'Venda', 'Vietnamese', 'Volapük', 'Walloon', 'Wolof', 'Xhosa', 'Yiddish', 'Yoruba', 'Zhuang; Chuang', 'Chinese', 'Zulu'];
    let lang_code = { 'Afar': 'aa', 'Abkhazian': 'ab', 'Avestan': 'ae', 'Afrikaans': 'af', 'Akan': 'ak', 'Amharic': 'am', 'Aragonese': 'an', 'Arabic': 'ar', 'Assamese': 'as', 'Avaric': 'av', 'Aymara': 'ay', 'Azerbaijani': 'az', 'Bashkir': 'ba', 'Belarusian': 'be', 'Bulgarian': 'bg', 'Bihari languages': 'bh', 'Bislama': 'bi', 'Bambara': 'bm', 'Bengali': 'bn', 'Tibetan': 'bo', 'Breton': 'br', 'Bosnian': 'bs', 'Catalan; Valencian': 'ca', 'Chechen': 'ce', 'Chamorro': 'ch', 'Corsican': 'co', 'Cree': 'cr', 'Czech': 'cs', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic': 'cu', 'Chuvash': 'cv', 'Welsh': 'cy', 'Danish': 'da', 'German': 'de', 'Divehi; Dhivehi; Maldivian': 'dv', 'Dzongkha': 'dz', 'Ewe': 'ee', 'Greek, Modern (1453-)': 'el', 'English': 'en', 'Esperanto': 'eo', 'Spanish': 'es', 'Estonian': 'et', 'Basque': 'eu', 'Persian': 'fa', 'Fulah': 'ff', 'Finnish': 'fi', 'Fijian': 'fj', 'Faroese': 'fo', 'French': 'fr', 'Western Frisian': 'fy', 'Irish': 'ga', 'Gaelic; Scottish Gaelic': 'gd', 'Galician': 'gl', 'Guarani': 'gn', 'Gujarati': 'gu', 'Manx': 'gv', 'Hausa': 'ha', 'Hebrew': 'he', 'Hindi': 'hi', 'Hiri Motu': 'ho', 'Croatian': 'hr', 'Haitian; Haitian Creole': 'ht', 'Hungarian': 'hu', 'Armenian': 'hy', 'Herero': 'hz', 'Interlingua (International Auxiliary Language Association)': 'ia', 'Indonesian': 'id', 'Interlingue; Occidental': 'ie', 'Igbo': 'ig', 'Sichuan Yi; Nuosu': 'ii', 'Inupiaq': 'ik', 'Ido': 'io', 'Icelandic': 'is', 'Italian': 'it', 'Inuktitut': 'iu', 'Japanese': 'ja', 'Javanese': 'jv', 'Georgian': 'ka', 'Kongo': 'kg', 'Kikuyu; Gikuyu': 'ki', 'Kuanyama; Kwanyama': 'kj', 'Kazakh': 'kk', 'Kalaallisut; Greenlandic': 'kl', 'Central Khmer': 'km', 'Kannada': 'kn', 'Korean': 'ko', 'Kanuri': 'kr', 'Kashmiri': 'ks', 'Kurdish': 'ku', 'Komi': 'kv', 'Cornish': 'kw', 'Kirghiz; Kyrgyz': 'ky', 'Latin': 'la', 'Luxembourgish; Letzeburgesch': 'lb', 'Ganda': 'lg', 'Limburgan; Limburger; Limburgish': 'li', 'Lingala': 'ln', 'Lao': 'lo', 'Lithuanian': 'lt', 'Luba-Katanga': 'lu', 'Latvian': 'lv', 'Malagasy': 'mg', 'Marshallese': 'mh', 'Maori': 'mi', 'Macedonian': 'mk', 'Malayalam': 'ml', 'Mongolian': 'mn', 'Marathi': 'mr', 'Malay': 'ms', 'Maltese': 'mt', 'Burmese': 'my', 'Nauru': 'na', 'Bokmål, Norwegian; Norwegian Bokmål': 'nb', 'Ndebele, North; North Ndebele': 'nd', 'Nepali': 'ne', 'Ndonga': 'ng', 'Dutch; Flemish': 'nl', 'Norwegian Nynorsk; Nynorsk, Norwegian': 'nn', 'Norwegian': 'no', 'Ndebele, South; South Ndebele': 'nr', 'Navajo; Navaho': 'nv', 'Chichewa; Chewa; Nyanja': 'ny', 'Occitan (post 1500)': 'oc', 'Ojibwa': 'oj', 'Oromo': 'om', 'Oriya': 'or', 'Ossetian; Ossetic': 'os', 'Panjabi; Punjabi': 'pa', 'Pali': 'pi', 'Polish': 'pl', 'Pushto; Pashto': 'ps', 'Portuguese': 'pt', 'Quechua': 'qu', 'Romansh': 'rm', 'Rundi': 'rn', 'Romanian; Moldavian; Moldovan': 'ro', 'Russian': 'ru', 'Kinyarwanda': 'rw', 'Sanskrit': 'sa', 'Sardinian': 'sc', 'Sindhi': 'sd', 'Northern Sami': 'se', 'Sango': 'sg', 'Sinhala; Sinhalese': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Samoan': 'sm', 'Shona': 'sn', 'Somali': 'so', 'Albanian': 'sq', 'Serbian': 'sr', 'Swati': 'ss', 'Sotho, Southern': 'st', 'Sundanese': 'su', 'Swedish': 'sv', 'Swahili': 'sw', 'Tamil': 'ta', 'Telugu': 'te', 'Tajik': 'tg', 'Thai': 'th', 'Tigrinya': 'ti', 'Turkmen': 'tk', 'Tagalog': 'tl', 'Tswana': 'tn', 'Tonga (Tonga Islands)': 'to', 'Turkish': 'tr', 'Tsonga': 'ts', 'Tatar': 'tt', 'Twi': 'tw', 'Tahitian': 'ty', 'Uighur; Uyghur': 'ug', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uzbek': 'uz', 'Venda': 've', 'Vietnamese': 'vi', 'Volapük': 'vo', 'Walloon': 'wa', 'Wolof': 'wo', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zhuang; Chuang': 'za', 'Chinese': 'zh', 'Zulu': 'zu' };
    lang_name = capitalize(lang_name);

    for (l in lang) {
        if (lang_name == l) {
            break;
        }
    }
    recognition.lang = lang_code[lang_name];
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}