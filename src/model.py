import torch
import torch.nn as nn
import torch.nn.functional as F


# class maxpool(nn.Module):
#     def __init__(self):
#         super(maxpool, self).__init__()
#         self.main = nn.MaxPool2d(2, 2)
# 
#     def forward(self, input):
#         out = self.main(input)
#         return out


# class upconv(nn.Module):
#     def __init__(self, in_ch):
#         super(maxpool, self).__init__()
#         self.main = nn.ConvTranspose2d(in_ch, in_ch / 2, 2, 2)
#     
#     def forward(self, input):
#         out = self.main(input)
#         return out


# class last_conv(nn.Module):
#     def __init__(self, in_ch, out_ch):
#         super(last_conv, self).__init__()
# 
#     def forward(self, input):
#         out = self.main(input)
#         return out

# def concat(input, skip):
#     assert input.shape[2] == input.shape[3], 'Not match w and h of input size.'
#     in_s = input.shape[2]
#     sk_s = skip.shape[2]
#     cr_sta = int(sk_s/2 - in_s/2)
#     cr_end = int(sk_s/2 + in_s/2)
#     cropped = skip[:, :, cr_sta:cr_end, cr_sta:cr_end]
#     out = torch.cat((input, cropped), 1)
#     return out

def concat(input, skip):
    out = torch.cat([input, F.upsample(skip, input.size()[2:], mode='bilinear')], 1)
    return out

class two_conv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(two_conv, self).__init__()
        self.main = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 3),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(True),
                nn.Conv2d(out_ch, out_ch, 3),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(True),
                )

    def forward(self, input):
        out = self.main(input)
        return out


class encode(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(encode, self).__init__()
        self.conv = two_conv(in_ch, out_ch)
        self.maxpool = nn.MaxPool2d(2, 2)

    def forward(self, input):
        out_conv = self.conv(input)
        out = self.maxpool(out_conv)
        return out, out_conv


class decode(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(decode, self).__init__()
        self.upconv = nn.ConvTranspose2d(in_ch, int(in_ch/2), 2, 2)
        self.conv = two_conv(in_ch, out_ch)

    def forward(self, input, skip):
        out = self.upconv(input)
        out = concat(out, skip)
        out = self.conv(out)

        return out


class UNet(nn.Module):
    def __init__(self):
        super(Unet, self).__init__()
        self.encode1 = encode(3, 64)
        self.encode2 = encode(64, 128)
        self.encode3 = encode(128, 256)
        self.encode4 = encode(256, 512)
        self.two_conv = two_conv(512, 1024)
        self.decode1 = decode(1024, 512)
        self.decode2 = decode(512, 256)
        self.decode3 = decode(256, 128)
        self.decode4 = decode(128, 64)
        self.conv = nn.Conv2d(64, 21, 1)

    def forward(self, input):
        # print('in: {}'.format(input.shape))
        out, skip1 = self.encode1(input)
        out, skip2 = self.encode2(out)
        out, skip3 = self.encode3(out)
        out, skip4 = self.encode4(out)
        out = self.two_conv(out)
        out = self.decode1(out, skip4)
        out = self.decode2(out, skip3)
        out = self.decode3(out, skip2)
        out = self.decode4(out, skip1)
        out = self.conv(out)
        # print('out: {}'.format(out.shape))
        
        return out

