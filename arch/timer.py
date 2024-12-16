from datetime import datetime


def notify(app_name: str, summary: str, body: str):
    import gi

    gi.require_version("Notify", "0.7")

    from gi.repository import Notify  # noqa

    Notify.init(app_name)
    Notify.Notification.new(summary, body).show()


def notify_time():
    now = datetime.now()
    _day = now.strftime("%Y-%m-%d")
    _time = now.strftime("%H:%M:%S")
    notify("时间提醒", _time, _day)


def get_cron_kwargs(cron_str: str):
    cols = ("second", "minute", "hour", "day", "month", "day_of_week", "year")
    return {k: v for k, v in zip(cols, cron_str.split())}


if __name__ == "__main__":
    # APScheduler BlockingScheduler
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()

    notify("py定时任务", "时间提醒", "已启动")
    scheduler.add_job(notify_time, "cron", **get_cron_kwargs("0 0,30 * * * *"))

    scheduler.start()
