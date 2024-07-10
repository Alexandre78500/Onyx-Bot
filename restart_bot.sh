#!/bin/bash

SESSION_NAME="bot"
PROJECT_PATH="/home7/pikimi/onyx-bot"

# Vérifie si la session 'bot' existe déjà
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  # Si la session n'existe pas, en crée une nouvelle et démarre le bot
  tmux new-session -d -s $SESSION_NAME
  tmux send-keys -t $SESSION_NAME "cd $PROJECT_PATH" C-m
  tmux send-keys -t $SESSION_NAME "source venv/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME "python3 bot.py" C-m
else
  # Si la session existe, la kill et en crée une nouvelle pour démarrer le bot
  tmux kill-session -t $SESSION_NAME
  tmux new-session -d -s $SESSION_NAME
  tmux send-keys -t $SESSION_NAME "cd $PROJECT_PATH" C-m
  tmux send-keys -t $SESSION_NAME "source venv/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME "python3 bot.py" C-m
fi
