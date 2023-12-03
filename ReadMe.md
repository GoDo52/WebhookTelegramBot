# VoIP SMS Gateway

This project is a VoIP SMS gateway that allows users to rent virtual phone numbers, send and receive SMS messages, and handle crypto payments using the NowPayments API.

## Table of Contents
- [Introduction](#introduction)
- [Files](#files)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The VoIP SMS Gateway project provides a platform for users to interact with virtual phone numbers, send and receive SMS messages, and manage crypto payments. It includes modules for handling VoIP numbers, SMS functionalities, crypto payments via NowPayments, and a SQLite database for user and transaction management.

## Files

### 1. `setup.py`

The setup file contains configurations and API keys for the project.

### 2. `nowpayments.py`

The NowPayments module (`nowpayments.py`) includes functions for interacting with the NowPayments API, such as checking API status, creating invoices, and handling crypto payments. The `CryptoPayment` class represents a crypto payment.

### 3. `database.py`

The database module (`database.py`) includes SQLite operations for managing user information and transaction history. It defines the `User` class for user-related operations and initializes the SQLite database.

### 4. `smsapi.py`

The SMS API module (`smsapi.py`) provides functionalities for sending and receiving SMS messages using virtual phone numbers. It includes classes for `VirtualNumber` and `MdnMessage` representing virtual numbers and SMS messages, respectively. Additionally, it offers short-term and long-term SMS-related functions.

## Installation

To install and set up the VoIP SMS Gateway project, follow these steps:

1. Clone the repository.
2. Install the required dependencies.
3. Configure the API keys and settings in `setup.py`.

## Usage

The project can be used to:

- Rent virtual phone numbers and send/receive SMS messages.
- Handle crypto payments using the NowPayments API.
- Manage user information and transaction history in a SQLite database.

For detailed usage instructions, refer to the specific modules and functions in the code.

## Contributing

Contributions to the project are welcome. To contribute:

1. Fork the repository.
2. Make your changes.
3. Submit a pull request.

For bug reports or feature requests, please create an issue.