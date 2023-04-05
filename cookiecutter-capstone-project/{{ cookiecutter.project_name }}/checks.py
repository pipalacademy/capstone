from capstone_checker import register_check, main


@register_check()
def custom_check(context, args):
    # context: {"app_url": "...", "app_dir": "..."}
    # args: {"a": 1, "b": 2}  specified in capstone.yml
    pass


if __name__ == "__main__":
    main()
