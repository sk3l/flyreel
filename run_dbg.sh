#!/bin/bash
gunicorn --paste src/development.ini
