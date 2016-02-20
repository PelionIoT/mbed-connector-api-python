

/*

 * Copyright (c) 2015 ARM Limited. All rights reserved.

 * SPDX-License-Identifier: Apache-2.0

 * Licensed under the Apache License, Version 2.0 (the License); you may

 * not use this file except in compliance with the License.

 * You may obtain a copy of the License at

 *

 * http://www.apache.org/licenses/LICENSE-2.0

 *

 * Unless required by applicable law or agreed to in writing, software

 * distributed under the License is distributed on an AS IS BASIS, WITHOUT

 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

 * See the License for the specific language governing permissions and

 * limitations under the License.

 */

#ifndef __SECURITY_H__

#define __SECURITY_H__

 

#include <inttypes.h>

 

#define MBED_DOMAIN "582ff859-917c-49b3-aee6-3ee6f2f5cc6d"

#define MBED_ENDPOINT_NAME "64754207-5e02-4d03-904b-82151ad55ea6"

 

const uint8_t SERVER_CERT[] = "-----BEGIN CERTIFICATE-----\r\n"

"MIIBmDCCAT6gAwIBAgIEVUCA0jAKBggqhkjOPQQDAjBLMQswCQYDVQQGEwJGSTEN\r\n"

"MAsGA1UEBwwET3VsdTEMMAoGA1UECgwDQVJNMQwwCgYDVQQLDANJb1QxETAPBgNV\r\n"

"BAMMCEFSTSBtYmVkMB4XDTE1MDQyOTA2NTc0OFoXDTE4MDQyOTA2NTc0OFowSzEL\r\n"

"MAkGA1UEBhMCRkkxDTALBgNVBAcMBE91bHUxDDAKBgNVBAoMA0FSTTEMMAoGA1UE\r\n"

"CwwDSW9UMREwDwYDVQQDDAhBUk0gbWJlZDBZMBMGByqGSM49AgEGCCqGSM49AwEH\r\n"

"A0IABLuAyLSk0mA3awgFR5mw2RHth47tRUO44q/RdzFZnLsAsd18Esxd5LCpcT9w\r\n"

"0tvNfBv4xJxGw0wcYrPDDb8/rjujEDAOMAwGA1UdEwQFMAMBAf8wCgYIKoZIzj0E\r\n"

"AwIDSAAwRQIhAPAonEAkwixlJiyYRQQWpXtkMZax+VlEiS201BG0PpAzAiBh2RsD\r\n"

"NxLKWwf4O7D6JasGBYf9+ZLwl0iaRjTjytO+Kw==\r\n"

"-----END CERTIFICATE-----\r\n";

 

const uint8_t CERT[] = "-----BEGIN CERTIFICATE-----\r\n"

"MIIBzzCCAXOgAwIBAgIEKIozcjAMBggqhkjOPQQDAgUAMDkxCzAJBgNVBAYTAkZ\r\n"

"JMQwwCgYDVQQKDANBUk0xHDAaBgNVBAMME21iZWQtY29ubmVjdG9yLTIwMTYwHh\r\n"

"cNMTYwMjIwMDIyNzE2WhcNMTYxMjMxMDYwMDAwWjCBoTFSMFAGA1UEAxNJNTgyZ\r\n"

"mY4NTktOTE3Yy00OWIzLWFlZTYtM2VlNmYyZjVjYzZkLzY0NzU0MjA3LTVlMDIt\r\n"

"NGQwMy05MDRiLTgyMTUxYWQ1NWVhNjEMMAoGA1UECxMDQVJNMRIwEAYDVQQKEwl\r\n"

"tYmVkIHVzZXIxDTALBgNVBAcTBE91bHUxDTALBgNVBAgTBE91bHUxCzAJBgNVBA\r\n"

"YTAkZJMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEckAzj/W8lGZ90QpP2T67n\r\n"

"U4yL81dRdo1dlkr/twFAsyFdaS2BLoJHbfTIMEHm+sCM+l0KwQ8pC4sFCk34Pe4\r\n"

"8zAMBggqhkjOPQQDAgUAA0gAMEUCIQCJMklqBK1Z3U2fYC8jm/8s9YEPciwtDs6\r\n"

"epQZqazpRlgIgBKxj0IOS9x6oMnXA37Fpi6mcYqLdLcjmFfVmf+ehUOM=\r\n"

"-----END CERTIFICATE-----\r\n";

 

const uint8_t KEY[] = "-----BEGIN PRIVATE KEY-----\r\n"

"MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgpxM7n9WsqDp9SY3Q\r\n"

"tpHaY7HlCdnazZ2k65Fqpp3hOUKhRANCAARyQDOP9byUZn3RCk/ZPrudTjIvzV1F\r\n"

"2jV2WSv+3AUCzIV1pLYEugkdt9MgwQeb6wIz6XQrBDykLiwUKTfg97jz\r\n"

"-----END PRIVATE KEY-----\r\n";

 

#endif //__SECURITY_H__
