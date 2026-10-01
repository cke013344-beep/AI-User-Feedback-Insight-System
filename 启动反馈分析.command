#!/bin/zsh
# Double-click in Finder. Only stores the key after the user chooses to enter it.
cd -- "${0:A:h}" || exit 1
umask 077
mkdir -p local_data
if [[ -z "$OPENROUTER_API_KEY" && ! -s local_data/.openrouter_key ]]; then
  print '首次启动：请粘贴有效的 OpenRouter 密钥，然后按回车。'
  print '输入不会显示。直接按回车可跳过，先使用关键词分类。'
  print '密钥将存于此电脑 local_data/.openrouter_key；不要把 local_data 文件夹分享给别人。'
  read -rs 'feedback_api_key?密钥：'
  print
  if [[ -n "$feedback_api_key" ]]; then
    print -rn -- "$feedback_api_key" > local_data/.openrouter_key
    chmod 600 local_data/.openrouter_key
  fi
  unset feedback_api_key
fi
if ! command -v python3 >/dev/null; then
  print '未找到 python3。请先安装 Python 3.9 或更高版本。'
  read 'feedback_finish?按回车关闭。'
  exit 1
fi
python3 web_app.py --provider openrouter --port 0 --open
print '应用已停止。历史记录保留。'
read 'feedback_finish?按回车关闭此窗口。'
