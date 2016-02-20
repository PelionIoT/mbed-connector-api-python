export MBED_USER_ID=mdc-api-python
cd mdc_api/tests/bin
git clone https://github.com/bridadan/mbed-client-linux-example.git
rm mbed-client-linux-example/source/security.h
cp ./security.h mbed-client-linux-example/source/security.h
ls
cd mbed-client-linux-example
echo "{\"endpoint-lifetime\": 60}" > config.json
yotta target x86-linux-native
yotta build