from plugins import verify_impl,plugin_return

# class Plugin1:
@verify_impl
def run_verify(index, row):
    print(f"inside Plugin1 {index} {row}")