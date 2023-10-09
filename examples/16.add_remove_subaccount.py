from config import TEST_ACCT_KEY, TEST_SUB_ACCT_KEY, TEST_NETWORK
from bluefin_v2_client import (
    BluefinClient,
    Networks,
)
import asyncio


async def main():
  # initialize the parent account client
  clientParent = BluefinClient(True, Networks[TEST_NETWORK], TEST_ACCT_KEY)
  await clientParent.init(True)

  # initialize the child account client
  clientChild = BluefinClient(True, Networks[TEST_NETWORK], TEST_SUB_ACCT_KEY)
  await clientChild.init(True)

  print("Parent: ", clientParent.get_public_address())
  print("Child: ", clientChild.get_public_address())

  # add child account as subaccount
  status = await clientParent.update_sub_account(
      clientChild.get_public_address(), True
    )
  print("Sub account added: {}\n".format(status))

  # remove child account as subaccount
  status = await clientParent.update_sub_account(
      clientChild.get_public_address(), True
    )
  print("Sub account removed: {}\n".format(status))


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
  loop.close()