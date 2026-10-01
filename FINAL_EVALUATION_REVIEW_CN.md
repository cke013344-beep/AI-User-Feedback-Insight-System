# 新评估样本：20 条中文审核表

**项目负责人已于 2026-10-02 确认 20 条全部 KEEP，参考答案已冻结。** 以下答案由助手读原评论起草；请先审核，不能称为独立多人标注。中文仅用于帮助理解，英文原文和参考字段为准。

确认每条的分类、主题、严重程度、需求和引用。认可填 KEEP；要修改填 CHANGE 并说明；不确定填 UNSURE。你也可以直接回复“全部 KEEP”或列出要讨论的编号，我会记录。

特别留意 H001（播放反复中断，medium）、H013（已付费内容无法访问，high）、H014（报价不同但未扣费，low）。它们体现边界规则，允许讨论。

## H001（来源 UID 75267，calm）

> Regularly closes mid session and stops the meditations meaning that you can be sat thinking the session is still on whilst really the app has crashed.  and a waste of money.

**中文理解与判断：** 冥想时经常退出，导致播放中断；反复干扰，但未说完全不能使用。

**参考分类：** `BUG`　**主题：** `CRASH_PERFORMANCE`　**严重程度：** `medium`

**参考需求：** Complete meditation sessions without the app closing unexpectedly.

**参考引用：**

> Regularly closes mid session and stops the meditations

**你的决定：** KEEP（项目负责人在运行前确认）。

## H002（来源 UID 135810，digitalwellbeing）

> It is causing a glitch in the settings interface of my OnePlus 8t device after updating the app. What is the problem?????? Reply.....

**中文理解与判断：** 更新后手机设置界面出现故障；没有说明整个手机不能用。

**参考分类：** `BUG`　**主题：** `FUNCTION_FAILURE`　**严重程度：** `medium`

**参考需求：** Use the phone settings interface without glitches after the app update.

**参考引用：**

> causing a glitch in the settings interface

**你的决定：** KEEP（项目负责人在运行前确认）。

## H003（来源 UID 137543，digitalwellbeing）

> made my pixel unusable. cant make calls and ui always crashes to the point whrre i have to force restart every day

**中文理解与判断：** 手机无法正常使用，不能打电话，并经常需要强制重启。

**参考分类：** `BUG`　**主题：** `CRASH_PERFORMANCE`　**严重程度：** `high`

**参考需求：** Use the phone and make calls without crashes or forced restarts.

**参考引用：**

> made my pixel unusable. cant make calls

**你的决定：** KEEP（项目负责人在运行前确认）。

## H004（来源 UID 52819，headspace）

> App is freezing a lot ..pls look into it..I have paid for an year and now i am unable to use the app

**中文理解与判断：** 应用频繁卡死，明确说现在无法使用；付款不是主要问题。

**参考分类：** `BUG`　**主题：** `CRASH_PERFORMANCE`　**严重程度：** `high`

**参考需求：** Use the app without it freezing.

**参考引用：**

> now i am unable to use the app

**你的决定：** KEEP（项目负责人在运行前确认）。

## H005（来源 UID 159766，daylio）

> I subscribed to this app for the sake of unlimited reminders which doesn't work. Useless app!!!

**中文理解与判断：** 已订阅但提醒功能失效；主要问题是提醒不工作。

**参考分类：** `BUG`　**主题：** `NOTIFICATIONS`　**严重程度：** `medium`

**参考需求：** Have the unlimited reminders work as expected.

**参考引用：**

> unlimited reminders which doesn't work

**你的决定：** KEEP（项目负责人在运行前确认）。

## H006（来源 UID 45423，headspace）

> Great experience for a beginner in meditation like me. There's only one thing, I have to log in every time I open the app. It gets annoying so if you can fix that, it'll be a deserving 5-star.

**中文理解与判断：** 每次打开都要重新登录；仍能登录，但重复操作造成干扰。

**参考分类：** `ACCOUNT`　**主题：** `ACCOUNT_ACCESS`　**严重程度：** `medium`

**参考需求：** Stay signed in between app sessions.

**参考引用：**

> I have to log in every time I open the app.

**你的决定：** KEEP（项目负责人在运行前确认）。

## H007（来源 UID 50420，headspace）

> I can't sign up or log in, it always says "something went wrong try again". I'm uninstalling the app.

**中文理解与判断：** 无法注册或登录，提示出错。

**参考分类：** `ACCOUNT`　**主题：** `ACCOUNT_ACCESS`　**严重程度：** `high`

**参考需求：** Sign up or log in without the repeated error message.

**参考引用：**

> I can't sign up or log in

**你的决定：** KEEP（项目负责人在运行前确认）。

## H008（来源 UID 51416，headspace）

> I would rate this a zero if I could it doesn't let me sign in and it says try again later I try later it still doesn't work I got this app to stop stress but it's just causing so much more

**中文理解与判断：** 反复无法登录，等待后仍不成功。

**参考分类：** `ACCOUNT`　**主题：** `ACCOUNT_ACCESS`　**严重程度：** `high`

**参考需求：** Sign in successfully instead of repeatedly being told to try later.

**参考引用：**

> it doesn't let me sign in

**你的决定：** KEEP（项目负责人在运行前确认）。

## H009（来源 UID 54554，headspace）

> Whenever I try to log in or create a new account it keeps saying something went wrong.

**中文理解与判断：** 登录或创建账户均提示出错，无法完成账户访问。

**参考分类：** `ACCOUNT`　**主题：** `ACCOUNT_ACCESS`　**严重程度：** `high`

**参考需求：** Log in or create an account without an error.

**参考引用：**

> Whenever I try to log in or create a new account it keeps saying something went wrong.

**你的决定：** KEEP（项目负责人在运行前确认）。

## H010（来源 UID 53251，headspace）

> Hey Headspace Your app wont let me login to my account and everytime i press "Forgot Password" it will say "something went wrong" and i know i had an account last night. Can you care to explain please??

**中文理解与判断：** 不能登录，忘记密码功能也报错。

**参考分类：** `ACCOUNT`　**主题：** `ACCOUNT_ACCESS`　**严重程度：** `high`

**参考需求：** Regain account access and use the password recovery option.

**参考引用：**

> Your app wont let me login to my account

**你的决定：** KEEP（项目负责人在运行前确认）。

## H011（来源 UID 97124，fabulous）

> Installed and then Uninstalled in less than 5 minutes. There is a charge for this app. The price isn't terrible, but I don't want to pay for it.

**中文理解与判断：** 不愿付费，没有描述错误扣费或实际财产损失。

**参考分类：** `PAYMENT`　**主题：** `PRICING_SUBSCRIPTION`　**严重程度：** `low`

**参考需求：** Use the app without paying a fee.

**参考引用：**

> I don't want to pay for it.

**你的决定：** KEEP（项目负责人在运行前确认）。

## H012（来源 UID 89133，fabulous）

> Really bad! Uninspiring programs that don't inspire and aren't personally tailored. Also charged me before the trial period finished and made it quite a challenge to submit a request for reimbursement.

**中文理解与判断：** 试用结束前被扣费，申请退款也困难；主要诉求是争议扣费。

**参考分类：** `PAYMENT`　**主题：** `CHARGES_REFUNDS`　**严重程度：** `high`

**参考需求：** Resolve the charge made before the trial ended and obtain reimbursement.

**参考引用：**

> charged me before the trial period finished

**你的决定：** KEEP（项目负责人在运行前确认）。

## H013（来源 UID 48370，headspace）

> i have subscribed this app 10 days back and still i cant unlock the videos under the subscription. i have tried to contact them but nothing has helped.

**中文理解与判断：** 付费十天后订阅内容仍锁定；属于付费访问问题，核心内容不可用。

**参考分类：** `PAYMENT`　**主题：** `PRICING_SUBSCRIPTION`　**严重程度：** `high`

**参考需求：** Access the videos covered by the paid subscription.

**参考引用：**

> still i cant unlock the videos under the subscription

**你的决定：** KEEP（项目负责人在运行前确认）。

## H014（来源 UID 49012，headspace）

> Seems to be a bug. I checked online and it says the subscription is $12.99/month but when I try to buy through the app it says $120/month!

**中文理解与判断：** 网页和应用报价不一致，但没有说明已经扣费；暂按未发生损失的价格问题。

**参考分类：** `PAYMENT`　**主题：** `PRICING_SUBSCRIPTION`　**严重程度：** `low`

**参考需求：** See a consistent and accurate subscription price online and in the app.

**参考引用：**

> online and it says the subscription is $12.99/month but when I try to buy through the app it says $120/month!

**你的决定：** KEEP（项目负责人在运行前确认）。

## H015（来源 UID 45083，headspace）

> I absolutely love the sleepcasts and they provided skme much needed relief while I was away from home for university, my only grievance is that after the free trial ended i no longer had access to the full versions and couldn't afford the monthly subscription.

**中文理解与判断：** 试用结束后无法负担订阅，属于价格和付费墙诉求。

**参考分类：** `PAYMENT`　**主题：** `PRICING_SUBSCRIPTION`　**严重程度：** `low`

**参考需求：** Access sleepcasts at an affordable price after the free trial.

**参考引用：**

> couldn't afford the monthly subscription.

**你的决定：** KEEP（项目负责人在运行前确认）。

## H016（来源 UID 156815，daylio）

> Love it for Journaling and mood tracking. I wish it gave more averages by numbers than bars and charts.

**中文理解与判断：** 希望新增数值平均值展示，而不只显示图表。

**参考分类：** `FEATURE_UX`　**主题：** `FEATURE_REQUEST`　**严重程度：** `low`

**参考需求：** View numerical averages alongside the existing charts.

**参考引用：**

> I wish it gave more averages by numbers than bars and charts.

**你的决定：** KEEP（项目负责人在运行前确认）。

## H017（来源 UID 136621，digitalwellbeing）

> Superfluous app with no option to uninstall or disable. Google is turning into Samsung or Apple.

**中文理解与判断：** 无法卸载或禁用；是明确的移除限制。

**参考分类：** `FEATURE_UX`　**主题：** `INSTALL_REMOVAL`　**严重程度：** `medium`

**参考需求：** Uninstall or disable the unwanted app.

**参考引用：**

> no option to uninstall or disable

**你的决定：** KEEP（项目负责人在运行前确认）。

## H018（来源 UID 159621，daylio）

> Good app... If you could add timings to each day for each event that would be nice.

**中文理解与判断：** 希望每个事件能记录时间，是可选的新功能。

**参考分类：** `FEATURE_UX`　**主题：** `FEATURE_REQUEST`　**严重程度：** `low`

**参考需求：** Add a time to each event in the daily record.

**参考引用：**

> If you could add timings to each day for each event

**你的决定：** KEEP（项目负责人在运行前确认）。

## H019（来源 UID 48879，headspace）

> i would like it if i could get exactly how much time i have meditated. i know it tells me (X) amount of hours but if it was down to the minute as well, well that would be awesome.

**中文理解与判断：** 希望总冥想时长精确到分钟，是功能改进建议。

**参考分类：** `FEATURE_UX`　**主题：** `FEATURE_REQUEST`　**严重程度：** `low`

**参考需求：** View total meditation time down to the minute.

**参考引用：**

> if it was down to the minute as well

**你的决定：** KEEP（项目负责人在运行前确认）。

## H020（来源 UID 135416，digitalwellbeing）

> I now have to manually monitor my app updates as I cannot disable this app and do not want to download updates for it. Allowing ot to be disabled would be extremely helpful.

**中文理解与判断：** 不能禁用应用，因而需要手动管理更新；明确造成操作负担。

**参考分类：** `FEATURE_UX`　**主题：** `INSTALL_REMOVAL`　**严重程度：** `medium`

**参考需求：** Disable the app to avoid having to manually manage its updates.

**参考引用：**

> I cannot disable this app

**你的决定：** KEEP（项目负责人在运行前确认）。
