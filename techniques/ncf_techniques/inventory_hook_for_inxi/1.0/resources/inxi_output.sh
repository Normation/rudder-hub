#!/bin/bash
echo "{ \"inxi_output\": $(inxi --tty -ZSMCmnDPjBs --output json --output-file print) }" | sed -E 's/"[0-9#]+([^"]+":)/"\1/g'
