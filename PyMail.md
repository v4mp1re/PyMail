# PyMail

## Simple SMTP Mailer class

  

PyMail is a basic implementaion of SMTP mail

  
  

## Features

  

- Uses basic socket communication

- OOP based

  

This can be used as a reference for python socket based communication and SMTP protocol.

Please fork this code and extend the functionality.

  

### configure the following in .env file

  

- EMAIL_HOST

- EMAIL_HOST_USER

- EMAIL_HOST_PASSWORD

- EMAIL_PORT

  

## Usage

  

mail = Mail()

  

mail.mail_from('sender_email', 'name')

  

mail.to('recepient_email')

  

mail.subject('Subject')

  

mail.message('Message body')

  

mail.send()

  

## SSL configuration

  

This app loads default ssl context hence try to use system default ssl certificates.

  

execute the following command before running application for unix based systems.

### ls -s /etc/ssl path-to-python/etc/openssl