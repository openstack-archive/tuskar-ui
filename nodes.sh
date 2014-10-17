OUTPUT_FILE=nodes.csv
NODES_JSON_FILE=/home/stack/instackenv.json
NUM_NODES=`jq '.nodes | length' $NODES_JSON_FILE`

if [ -e $OUTPUT_FILE ]
then
    rm $OUTPUT_FILE
fi

for i in $(seq 0 `expr $NUM_NODES - 1`)
do
    DRIVER=`jq -r ".nodes[${i}] | .[\"pm_type\"]" $NODES_JSON_FILE`
    SSH_ADDRESS=`jq -r ".nodes[${i}] | .[\"pm_addr\"]" $NODES_JSON_FILE`
    SSH_USERNAME=`jq -r ".nodes[${i}] | .[\"pm_user\"]" $NODES_JSON_FILE`
    SSH_KEY_CONTENTS=`jq -r ".nodes[${i}] | .[\"pm_password\"]" $NODES_JSON_FILE`
    MAC=`jq -r ".nodes[${i}] | .mac[0]" $NODES_JSON_FILE`
    echo "${DRIVER},${SSH_ADDRESS},${SSH_USERNAME},\"${SSH_KEY_CONTENTS}\",${MAC}" >> $OUTPUT_FILE
done
