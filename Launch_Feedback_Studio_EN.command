#!/bin/zsh
# English launcher. Both language pages share local history and configuration.
cd -- "${0:A:h}" || exit 1
umask 077
mkdir -p local_data
if [[ -z "$OPENROUTER_API_KEY" && ! -s local_data/.openrouter_key ]]; then
  print 'First launch: paste your valid OpenRouter API key and press Enter.'
  print 'Input is hidden. Press Enter without a key to use keyword classification.'
  print 'The key is stored locally in local_data/.openrouter_key. Do not share local_data.'
  read -rs 'feedback_api_key?API key: '
  print
  if [[ -n "$feedback_api_key" ]]; then
    print -rn -- "$feedback_api_key" > local_data/.openrouter_key
    chmod 600 local_data/.openrouter_key
  fi
  unset feedback_api_key
fi
if ! command -v python3 >/dev/null; then
  print 'Python 3.9 or newer is required.'
  read 'feedback_finish?Press Enter to close.'
  exit 1
fi
python3 web_app.py --provider openrouter --language en --port 0 --open
print 'The launcher has finished. Saved history is retained.'
read 'feedback_finish?Press Enter to close this window.'
