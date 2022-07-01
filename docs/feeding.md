# Feeding

Feeding your data to **112centraal** or a custom endpoint can be set up with not too much of a problem.
Please refer to the <a href="/docs/config.md">Configuration</a> manual to learn how to configure feeding.

Whenever a request to an endpoint fails or takes too long to complete, it is silently discarded and should not further influence the other endpoints.

## Feeding to 112Centraal

**You want to help us out? Great!**
To prevent abuse and an overload of incoming data, access is moderated and possible feeders have to apply to join and receive their API key.

### Please apply <a href="https://112centraal.nl/apply" target="_blank">here</a>

## Feeding to custom URL's

Feeding to custom URL's is easy to set up, but requires some server-side setup.

Messages received by **Open112** are put in a queue which is pushed to all endpoints one-by-one. Every message is sent as a `HTTP POST` request and contains the following `POST` data using `application/x-www-form-urlencoded`:

**Example:** (Formatted for readability)
```json
message=A2 11124 Rit 89888 Joris Arien Ruijterstraat Middenbeemster
&capcodes=2029568,0126999,0123124
&timestamp=1656678655
&sent=1656678655
&version=2.3.0
```

Data can be used by, for example, PHP like this:
```php
$message = $_POST['message'];
$capcodes = explode(",", $_POST['capcodes']));
$msgtime = date("d-m-Y H:i:s", $_POST['timestamp'])
```

**No data you receive should be trusted by default!
Implement your own security checks to prevent abuse / corrupt data.**

### Fields

###### message
Contains the message as a string. Should not exceed 255 characters at any time but this is not guaranteed.

###### capcodes
Comma delimited list of capcodes which are always 7 digits long per capcode.

###### timestamp
Timestamp the alert was received by the receiver. Time is calculated client side and is not guaranteed to be correct.

###### sent
Timestamp the alert was actually SENT to the endpoint.

###### version
Open112 version, will be used at **112Centraal** to track and inform outdated feeders.
