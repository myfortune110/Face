# conding:utf-8

import mxnet as mx


def squeeze(data, num_filter, kernel=(1, 1), stride=(1, 1), pad=(0, 0), act_type="relu", mirror_attr={}):
    squeeze_1x1 = mx.symbol.Convolution(data=data, num_filter=num_filter, kernel=kernel, stride=stride, pad=pad)
    act = mx.symbol.Activation(data=squeeze_1x1, act_type=act_type, attr=mirror_attr)
    return act


def Fire_module(data, num_filter_squeeze, num_filter_fire, kernel_sequeeze=(1, 1), kernel_1x1=(1, 1),
                kernel_3x3=(3, 3), stride_squeeze=(1, 1), stride_1x1=(1, 1), stride_3x3=(1, 1),
                pad_1x1=(0, 0), pad_3x3=(1, 1), act_type="relu", mirror_attr={}):
    squeeze_1x1 = squeeze(data, num_filter_squeeze, kernel_sequeeze, stride_squeeze)
    expand1x1 = mx.symbol.Convolution(data=squeeze_1x1, num_filter=num_filter_fire, kernel=kernel_1x1,
                                      stride=stride_1x1, pad=pad_1x1)
    relu_expand1x1 = mx.symbol.Activation(data=expand1x1, act_type=act_type, attr=mirror_attr)

    expand3x3 = mx.symbol.Convolution(data=squeeze_1x1, num_filter=num_filter_fire, kernel=kernel_3x3,
                                      stride=stride_3x3, pad=pad_3x3)
    relu_expand3x3 = mx.symbol.Activation(data=expand3x3, act_type=act_type, attr=mirror_attr)
    return relu_expand1x1 + relu_expand3x3


def SqueezeNet(num_classes):
    data = mx.symbol.Variable(name='data')
    conv1 = mx.symbol.Convolution(data=data, num_filter=96, kernel=(7, 7), stride=(2, 2), pad=(0, 0))
    relu_conv1 = mx.symbol.Activation(data=conv1, act_type="relu", attr={})
    pool_conv1 = mx.symbol.Pooling(data=relu_conv1, kernel=(3, 3), stride=(2, 2), pool_type='max', attr={})

    fire2 = Fire_module(pool_conv1, num_filter_squeeze=16, num_filter_fire=64)
    fire3 = Fire_module(fire2, num_filter_squeeze=16, num_filter_fire=64)
    fire4 = Fire_module(fire3, num_filter_squeeze=32, num_filter_fire=128)

    pool4 = mx.symbol.Pooling(data=fire4, kernel=(3, 3), stride=(2, 2), pool_type='max', attr={})
    fire5 = Fire_module(pool4, num_filter_squeeze=32, num_filter_fire=128)
    fire6 = Fire_module(fire5, num_filter_squeeze=48, num_filter_fire=192)
    fire7 = Fire_module(fire6, num_filter_squeeze=48, num_filter_fire=192)
    fire8 = Fire_module(fire7, num_filter_squeeze=64, num_filter_fire=256)
    pool8 = mx.symbol.Pooling(data=fire8, kernel=(3, 3), stride=(2, 2), pool_type='max', attr={})
    fire9 = Fire_module(pool8, num_filter_squeeze=64, num_filter_fire=256)
    drop9 = mx.sym.Dropout(data=fire9, p=0.5)
    conv10 = mx.symbol.Convolution(data=drop9, num_filter=1000, kernel=(1, 1), stride=(1, 1), pad=(1, 1))
    relu_conv10 = mx.symbol.Activation(data=conv10, act_type="relu", attr={})
    pool10 = mx.symbol.Pooling(data=relu_conv10, kernel=(3, 3), pool_type='avg', attr={})

    flatten = mx.symbol.Flatten(data=pool10, name='flatten')


    # softmax = mx.symbol.SoftmaxOutput(data=flatten, name='softmax')
    fc = mx.sym.FullyConnected(data=flatten, num_hidden=num_classes, no_bias=False)
    return fc


def get_symbol(num_classes=10):
    # net = SqueezeNet(data=mx.symbol.Variable(name='data'), num_classes)
    net = SqueezeNet(num_classes)

    return net
