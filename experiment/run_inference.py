# Copyright (c) 2020 Software Platform Lab
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Software Platform Lab nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
from contextlib import closing

import pandas as pd
import torch

from utils import get_image_size, get_model, get_inference_wrapper, evaluate, eval_result_to_df

torch.backends.cudnn.benchmark = True

def main(args):
    # instantiate model and inputs
    image_size = get_image_size(args.model_name)
    input_shape = [args.bs, 3, image_size, image_size]
    model = get_model(args.model_name)
    dummy_input = torch.randn(*input_shape).cuda()

    with closing(get_inference_wrapper(model, dummy_input, args.mode)) as inference_wrapper:
        result = evaluate(inference_wrapper)

    df = eval_result_to_df(args.mode, result)
    if args.out_path:
        df.to_csv(args.out_path)
    else:
        summary = pd.DataFrame({'mean (ms)': df.mean(), 'stdev (ms)': df.std()})
        print(summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', type=str, help='Model name')
    parser.add_argument('--bs', type=int, default=1, help='batch size')
    parser.add_argument('--mode', type=str,
                        choices=['pytorch',
                                 'trace',
                                 'c2',
                                 'trt',
                                 'nimble',
                                 'nimble-multi'],
                        help='mode to conduct experiment')
    parser.add_argument('--out_path', type=str, default='', help='where to output the result')
    args = parser.parse_args()
    main(args)
