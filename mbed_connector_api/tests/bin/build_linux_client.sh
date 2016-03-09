export MBED_USER_ID=mdc-api-python
cd mbed_connector_api/tests/bin
git clone https://github.com/BlackstoneEngineering/mbed-client-linux-ci.git
rm mbed-client-linux-ci/source/security.h
cp ./security.h mbed-client-linux-ci/source/security.h
ls
cd mbed-client-linux-ci
echo "{\"endpoint-lifetime\": 60}" > config.json
yotta target x86-linux-native
yotta build