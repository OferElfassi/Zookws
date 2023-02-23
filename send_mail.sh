#!/bin/bash

TO="***"
SUBJECT="Test email"
BODY="Cookie value is: $1"

echo "$BODY" | mail -s "$SUBJECT" "$TO"

if [ $? -eq 0 ]; then
  echo "Email sent successfully."
else
  echo "Failed to send email."
fi
