#!/usr/bin/env python3

"""
This scripts converts PDF output from
Looker Studio to JPG image.
"""

from pdf2image import convert_from_path

# Open image
pdf = convert_from_path('./agents_and_precip.pdf')

# Have to loop over pdf...
for i in range(len(pdf)):
    # Save image
    pdf[i].save('agents_and_precip.jpg', 'JPEG')