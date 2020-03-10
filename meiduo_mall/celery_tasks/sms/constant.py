
# 短信验证码 过期时间
SMS_CODE_EXPIRETIME = 300


# 手机号码在redis中的过期时间,解决短时间内 向同一手机号重复发送短信 的问题
MOBILE_EXPIRETIME = 60

# 标识某一属性在 redis 中的使用次数,解决类似于抽奖次数的问题
MOBILE_FREQUENCY = 1
