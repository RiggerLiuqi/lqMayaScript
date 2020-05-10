# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    DivisionRemainder
# .@Author:      CousinRig67
# .@Date:        2020-03-28
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#


import pymel.core as pm


def createDivisionLocNode(file_Name = 'file1'):
    f1 = pm.PyNode(file_Name)

    imageNumber = f1.attr('frameExtension')
    frameOffset = f1.attr('frameOffset')
    userFrame = f1.attr('useFrameExtension')
    return f1, imageNumber, frameOffset, userFrame


def positiveIntegerDivision():
    u"""
    整数除法得到商和余数，链接Maya节点
    :param dividendNumber: int
    :param divisorNumber:  int
    :return: [consult, remainder]
    """

    locator = pm.spaceLocator(n = 'divisionValue_record_loc')

    newAttr_Lists = ['dividend', 'divisor', 'consult', 'remainder', 'intNum', 'offsetFrame']
    for newAttr in newAttr_Lists:
        if newAttr == 'divisor':
            locator.addAttr(newAttr, dv = 1, at = 'double', min = 0.001, k = True)
        else:
            locator.addAttr(newAttr, dv = 0, at = 'long', min = 0, k = True)
    dividend = locator.attr('dividend')
    locator.setAttr('divisor', 1, clamp = True)
    divisor = locator.attr('divisor')
    consult = locator.attr('consult')
    remainder = locator.attr('remainder')
    intNum = locator.attr('intNum')
    offsetFrame = locator.attr('offsetFrame')

    dividendNumber = dividend.get()
    # divisorNumber = divisor.set(divisorNumber)

    # 被除数 / 除数 ==  带小数的商
    dividend_divisor_div_MPD = pm.createNode('multiplyDivide', n = 'dividend_divisor_div_MPD')
    dividend_divisor_div_MPD.operation.set(2)
    dividend.connect(dividend_divisor_div_MPD.input1.input1X)
    divisor.connect(dividend_divisor_div_MPD.input2.input2X)
    dividend_divisor_div_MPD.output.outputX.connect(intNum)

    # 判断带小数的商 与 四舍五入的数的大小
    fact_consult_CDT = pm.createNode('condition', n = 'fact_consult_CDT')
    fact_consult_CDT.operation.set(3)
    fact_consult_CDT.colorIfTrueR.set(0)
    fact_consult_CDT.colorIfFalseR.set(1)
    dividend_divisor_div_MPD.output.outputX.connect(fact_consult_CDT.firstTerm)
    intNum.connect(fact_consult_CDT.secondTerm)

    # 四舍五入的商 - （1|0） 得到整数部分的商
    int_consult_sub_PLUS = pm.createNode('plusMinusAverage', n = 'int_consult_sub_PLUS')
    int_consult_sub_PLUS.operation.set(2)
    intNum.connect(int_consult_sub_PLUS.input1D[0])
    fact_consult_CDT.outColor.outColorR.connect(int_consult_sub_PLUS.input1D[1])
    int_consult_sub_PLUS.output1D.connect(consult)

    # 整数的商 * 除数 == 少掉余数的积
    less_consult_multi_MPD = pm.createNode('multiplyDivide', n = 'less_consult_multi_MPD')
    less_consult_multi_MPD.operation.set(1)
    consult.connect(less_consult_multi_MPD.input1.input1X)
    divisor.connect(less_consult_multi_MPD.input2.input2X)

    # 被除数 - 少掉余数的积 == 余数
    remainder_sub_PlUS = pm.createNode('plusMinusAverage', n = 'remainder_sub_PlUS')
    remainder_sub_PlUS.operation.set(2)
    dividend.connect(remainder_sub_PlUS.input1D[0])
    less_consult_multi_MPD.output.outputX.connect(remainder_sub_PlUS.input1D[1])
    remainder_sub_PlUS.output1D.connect(remainder)

    return dividend, divisor, consult, remainder, offsetFrame


def imageNumber_value(file_name = 'file1'):
    u"""
    用于连接循环序列贴图， 被除数是总控，offsetFrame 是控制序列贴图 第一次循环偏移帧， 第二次走第一次重新开始循环
    :param file_name:
    :return:
    """
    myFiel = createDivisionLocNode(file_name)
    f1 = myFiel[0]
    imageNumber = myFiel[1]
    frameOffset = myFiel[2]
    userFrame = myFiel[3]

    div_loc = positiveIntegerDivision()
    dividend = div_loc[0]
    dividend_value = dividend.get()
    divisor = div_loc[1]
    consult = div_loc[2]
    remainder = div_loc[3]
    offsetFrame = div_loc[4]
    offsetFrame_value = offsetFrame.get()

    userFrame.set(1)

    # 分母
    denominator_sub_PLUS = pm.createNode('plusMinusAverage', n = 'denominator_sub_PLUS')
    denominator_sub_PLUS.operation.set(2)
    denominator_sub_PLUS.input1D[0].set(110)
    offsetFrame.connect(denominator_sub_PLUS.input1D[1])
    denominator_sub_PLUS.output1D.connect(divisor)

    # 分子
    dividend_value_sub_1_PLUS = pm.createNode('plusMinusAverage', n = 'dividend_value_sub_1_PLUS')
    dividend_value_sub_1_PLUS.operation.set(2)
    dividend.connect(dividend_value_sub_1_PLUS.input1D[0])
    offsetFrame.connect(dividend_value_sub_1_PLUS.input1D[1])

    # + 1 +  -offsetFrame
    framePlus_plus_1_PLUS = pm.createNode('plusMinusAverage', n = 'framePlus_plus_1_PLUS')
    framePlus_plus_1_PLUS.operation.set(1)

    # Dividend >= Divisor: + (-offsetFrame)
    # 当被除数大于或者等于除数时， 偏移帧增加 负的偏移帧，也就是下一个循环序列回到 第一帧开始
    dividend_divisor_CDT = pm.createNode('condition', n = 'dividend_divisor_CDT')
    dividend_divisor_CDT.operation.set(3)
    dividend.connect(dividend_divisor_CDT.firstTerm)
    divisor.connect(dividend_divisor_CDT.secondTerm)
    offsetFrame.connect(dividend_divisor_CDT.colorIfTrueR)
    dividend_divisor_CDT.colorIfFalseR.set(0)

    negative_offset_multiply_MPD = pm.createNode('multiplyDivide', n = 'negative_offset_multiply_MPD')
    negative_offset_multiply_MPD.operation.set(1)
    negative_offset_multiply_MPD.input2X.set(-1)
    dividend_divisor_CDT.outColorR.connect(negative_offset_multiply_MPD.input1X)
    negative_offset_multiply_MPD.outputX.connect(framePlus_plus_1_PLUS.input1D[2])

    remainder.connect(framePlus_plus_1_PLUS.input1D[0])
    framePlus_plus_1_PLUS.input1D[1].set(1)
    framePlus_plus_1_PLUS.output1D.connect(imageNumber)

    offsetFrame.connect(frameOffset)


imageNumber_value()


