#!/bin/bash

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_SSDX="$HOME/.ssdx/vdx_reports"
LOCAL_VDX_P_DIR="$SCRIPT_DIR/vdx_reports"

YLW="\033[93m"
BYL="\033[1;93m"
RED="\033[91m"
BRD="\033[1;91m"
GRN="\033[32m"
BGN="\033[1;32m"
BLD="\033[1m"
RST="\033[0m"

while true; do
    clear
    echo -e "${BLD}==================================================${RST}"
    echo -e "              ${YLW}VDX${RST} REPORT RUNNER"
    echo -e "${BLD}==================================================${RST}"
    echo -e "  ${BLD}[1] Run vdx.py      (Saves to:${YLW} $USER_SSDX)${RST}"
    echo -e "  ${BLD}[2] Run vdx-p.py    (Saves to:${YLW} $LOCAL_VDX_P_DIR)${RST}"
    echo -e "  [${BRD}3${RST}] ${BLD}Exit${RST}"
    echo -e "${BLD}==================================================${RST}"
    read -p "$(echo -e "\n\n  ${BLD}Select an option (1-3): ${RST}")" choice

    case $choice in
        1)
            echo ""
            echo -e "Running ${BYL}vdx.py${RST} ..."
            cd "$SCRIPT_DIR" || exit
            python3 vdx.py
            echo ""
            read -p "Done. Press ${BGN}Enter${RST} to return to the menu."
            clear
            ;;
        2)
            echo ""
            echo -e "Running ${BYL}vdx-p.py${RST} ..."
            cd "$SCRIPT_DIR" || exit
            python3 vdx-p.py
            echo ""
            read -p "Done. Press ${BGN}Enter${RST} to return to the menu."
            clear
            ;;
        3)
            exit 0
            ;;
        *)
            echo -e "${BRD}Invalid${RST} choice. Please try again."
            sleep 2
            ;;
    esac
done