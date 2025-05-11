if is_nsfw_detected and not execution_config.get('skip_nsfw'):
    print('\n' + 'NSFW content detected but processing anyway...')
    # return None  # この行をコメントアウトする
