#!/bin/bash

# Setup a red prompt for root and a green one for users.
NORMAL="\[\e[0m\]"
RED="\[\e[1;31m\]"
GREEN="\[\e[1;32m\]"
if [ "$USER" = root ]; then
        PS1="$RED\h [$NORMAL\w$RED]# $NORMAL"
else
        PS1="$GREEN\h [$NORMAL\w$GREEN]\$ $NORMAL"
fi

# alias
alias ls='ls --color=auto'
alias grep='grep --color=auto'
