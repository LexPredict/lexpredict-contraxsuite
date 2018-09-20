#!/usr/bin/bash

function ask() {
    QUESTION=$1
    while true; do
        read -p "${QUESTION} (y/n)" -r ANSWER
        echo ""
        case ${ANSWER} in
            [Yy]* ) ASK_ANSWER="y"; return;;
            [Nn]* ) ASK_ANSWER="n"; return;;
        esac
    done
}
