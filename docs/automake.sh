#!/bin/sh

{ watchmedo-2.7 shell-command \
    -p '*.rst;*.py' \
    -R \
    -c echo \
    source ../django_otp
} | while read line; do make html; done
