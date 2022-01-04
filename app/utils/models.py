import os
import random
import re
import string
from collections import namedtuple
from typing import List

import arrow
import names
import pandas as pd
import requests
from pydantic import BaseModel, IPvAnyAddress

Song = namedtuple("Song", ['artist', 'track'])


def generate_password() -> str:
    # pw 6-50 chars, number, upper, & lower
    pattern = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,50}')

    password = ''
    length = random.randint(6, 50)
    while pattern.match(password) is None:
        password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
    return password


def get_postcode() -> int:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    df = pd.read_csv(os.path.join(dir_path, 'australian-postcodes-2021-04-23.csv'))
    return int(df.sample().Zip.values)


def get_ip() -> str:
    resp = requests.get('https://api.ipify.org?format=json')
    return resp.json().get('ip')


def get_phone_no() -> str:
    phone = "04## ### ###"
    n = phone.count('#')
    for _ in range(n):
        phone = phone.replace('#', str(random.randint(0, 9)), 1)
    return phone


class Account(BaseModel):
    email: str
    password: str
    firstname: str
    surname: str
    gender: str
    dob: int
    postcode: int
    phone: str

    @classmethod
    def generate(cls, email: str) -> 'Account':
        gender = random.choice(['Male', 'Female', 'Prefer not to say'])
        return cls(
            email=email,
            password=generate_password(),
            firstname=names.get_first_name(gender=gender.lower()),
            surname=names.get_last_name(),
            gender=gender,
            dob=random.randint(2021 - 30, 2021 - 18),
            postcode=get_postcode(),
            phone=get_phone_no(),
        )


class SessionResults(Account):
    votes: List[Song]
    created_at: arrow.Arrow = arrow.now()
    src_addr: IPvAnyAddress = get_ip()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {arrow.Arrow: lambda x: x.for_json()}

