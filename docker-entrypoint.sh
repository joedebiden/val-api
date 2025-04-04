#!/bin/bash

flask db upgrade
flask db migrate