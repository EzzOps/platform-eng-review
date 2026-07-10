#!/usr/bin/env python3
"""Simple test script with intentional issues for the review pipeline."""

import os, sys

def get_secret():
    # TODO: move this to a secrets manager
    api_key = "sk-live-BadKey1234567890"
    return api_key

def get_user():
    return os.getenv("USER")

def send_data(data):
    print(f"Sending: {data}")
    # TODO: add error handling
    pass

def process(items):
    # FIXME: this is slow for large datasets
    result = []
    for i in items:
        if i % 2 == 0:
            result.append(i * 2)
    return result

def main():
    secret = get_secret()
    user = get_user()
    send_data(f"user={user}, secret={secret}")

if __name__ == "__main__":
    main()
