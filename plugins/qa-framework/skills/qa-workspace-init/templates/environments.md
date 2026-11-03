# <Project name> – environments and access

No values here: only names. Values live in the env files the project keeps out of git and in the
Execute.io project environment variables.

## Environments

| Environment | Android app id | iOS bundle id | Network needs (VPN?) | Notes |
|---|---|---|---|---|
| staging | <…> | <…> | <…> | fixed staging OTP: <yes/no> |
| preprod | <…> | <…> | <…> | |
| prod | <…> | <…> | <…> | OTP entered by the QA member |

## Account types and variable names

| Account type | Variable (staging) | Variable (prod) | Notes |
|---|---|---|---|
| <prepaid> | <MSISDN_PREPAID> | <…> | |
| <postpaid> | <MSISDN_POSTPAID> | <…> | |
| <guest> | – | – | no login |

## Devices and targets

- Emulator/simulator: <names>; the agent logs in itself on staging through the project's login automation.
- BrowserStack App Live: user <BrowserStack user name>; default devices <Android model / OS>, <iPhone model / OS>;
  the QA member logs in on each device; use debug staging builds on Android if release builds hide the login
  screen.
- The QA member's own devices: <…>.

## Back Office and other data

<How Back Office data is looked up, who signs in, what an agent may read. TODO (ask QA)>
