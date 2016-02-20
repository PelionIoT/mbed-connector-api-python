cd test/bin
git clone https://github.com/bridadan/mbed-client-linux-example.git
rm mbed-client-linux-example/source/security.h
cp ./security.h mbed-client-linux-example/source/security.h
cd mbed-client-linux-example
echo "{\"endpoint-lifetime\": 60}" > config.json
yt target x86-linux-native
yt build