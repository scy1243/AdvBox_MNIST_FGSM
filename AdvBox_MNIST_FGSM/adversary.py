#coding=utf-8
# Copyright 2017 - 2018 Baidu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Defines a class that contains the original object, the target and the
adversarial example.
"""
import numpy as np
import  logging
logger=logging.getLogger(__name__)

class Adversary(object):
    """
    Adversary contains the original object, the target and the adversarial
    example.
    """

    def __init__(self, original, original_label=None):
        """
        :param original: The original instance, such as an image.
        :param original_label: The original instance's label.
        """
        assert original is not None

        self.original_label = original_label
        #定向攻击的目标
        self.target_label = None
        self.adversarial_label = None
        #保存原始数据 强制拷贝
        self.__original = np.copy(original)
        self.__target = None
        self.__is_targeted_attack = False
        #保存生成的对抗样本
        self.__adversarial_example = None
        self.__bad_adversarial_example = None

    def set_target(self, is_targeted_attack, target=None, target_label=None):
        """
        Set the target be targeted or untargeted.
        :param is_targeted_attack: bool
        :param target: The target.
        :param target_label: If is_targeted_attack is true and target_label is
                    None, self.target_label will be set by the Attack class.
                    If is_targeted_attack is false, target_label must be None.
        """
        assert (target_label is None) or is_targeted_attack
        self.__is_targeted_attack = is_targeted_attack
        self.target_label = target_label
        self.__target = target
        if not is_targeted_attack:
            self.target_label = None
            self.__target = None

    def set_original(self, original, original_label=None):
        """
        Reset the original.
        :param original: Original instance.
        :param original_label: Original instance's label.#原始实例的标签
        """
        if original != self.__original:
            self.__original = original
            self.original_label = original_label
            self.__adversarial_example = None
            self.__bad_adversarial_example = None
        if original is None:
            self.original_label = None
    
    #判断攻击是否成功，成功则会返回true，调用时括号里需要加参数
    def _is_successful(self, adversarial_label):
        """
        Is the adversarial_label is the expected adversarial label.
        :param adversarial_label: adversarial label.
        :return: bool
        """
        if self.target_label is not None:#用 is not None来判断对象是否有定义
            return adversarial_label == self.target_label
        else:
            return (adversarial_label is not None) and \
                   (adversarial_label != self.original_label)
    
    #self的调用方法，直接用这个函数，括号里不需要加参数
    def is_successful(self):
        """
        Has the adversarial example been found.
        :return: bool
        """
        return self._is_successful(self.adversarial_label)

    def try_accept_the_example(self, adversarial_example, adversarial_label):
        """
        If adversarial_label the target label that we are finding.
        The adversarial_example and adversarial_label will be accepted and
        True will be returned.
        :return: bool
        """
        assert adversarial_example is not None
        assert self.__original.shape == adversarial_example.shape

        ok = self._is_successful(adversarial_label)
        if ok:
            self.__adversarial_example = np.copy(adversarial_example)#如果攻击成功，则把adversarial_example复制过去
            self.adversarial_label = adversarial_label#同时复制对抗样本的标签
        else:
            self.__bad_adversarial_example = np.copy(adversarial_example)
        return ok

    def perturbation(self, multiplying_factor=1.0):#默认的乘系数是1，这个是用来看对抗样本与原图的差异，即扰动，如果想要更改扰动大小就可以用扰动乘以一个系数
        """
        The perturbation that the adversarial_example is added.
        :param multiplying_factor: float.
        :return: The perturbation that is multiplied by multiplying_factor.
        """
        assert self.__original is not None
        assert (self.__adversarial_example is not None) or \
               (self.__bad_adversarial_example is not None)
        if self.__adversarial_example is not None:#如果对抗样本不是空的话，则计算出和原始图片之间的差别并乘以系数
            return multiplying_factor * (
                self.__adversarial_example - self.__original)
        else:
            return multiplying_factor * (
                self.__bad_adversarial_example - self.__original)

    @property
    def is_targeted_attack(self):
        """
        :property: is_targeted_attack
        """
        return self.__is_targeted_attack

    @property
    def target(self):
        """
        :property: target
        """
        return self.__target

    @property
    def original(self):
        """
        :property: original
        """
        return self.__original

    @property
    def adversarial_example(self):#这个函数用来返回对抗样本
        """
        :property: adversarial_example
        """
        return self.__adversarial_example

    @property
    def bad_adversarial_example(self):
        """
        :property: bad_adversarial_example#这里的对抗样本是扰动了但是和原来图片标签相同的，也就是失败的
        """
        return self.__bad_adversarial_example
