#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class AuthenticationType(Enum):
    OTP = "OTP"

    def to_ams_dict(self):
        return self.name
