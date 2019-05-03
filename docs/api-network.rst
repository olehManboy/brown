.. _api-network:

===========
Network API
===========

.. py:attribute:: brownie.network


Accounts
========

Account classes should not be instantiated directly. The ``Accounts`` container is available as ``accounts`` (or just ``a``) and will create each ``Account`` automatically during initialization. Add more accounts using ``Accounts.add``.

Accounts
--------

.. py:class:: brownie.network.accounts.Accounts

    Singleton list-like container that holds all of the available accounts as ``Account`` or ``LocalAccount`` objects. When printed it will display as a list.

    .. code-block:: python

        >>> from brownie.network import accounts
        >>> accounts
        [<Account object '0x7Ebaa12c5d1EE7fD498b51d4F9278DC45f8D627A'>, <Account object '0x186f79d227f5D819ACAB0C529031036D11E0a000'>, <Account object '0xC53c27492193518FE9eBff00fd3CBEB6c434Cf8b'>, <Account object '0x2929AF7BBCde235035ED72029c81b71935c49e94'>, <Account object '0xb93538FEb07b3B8433BD394594cA3744f7ee2dF1'>, <Account object '0x1E563DBB05A10367c51A751DF61167dE99A4d0A7'>, <Account object '0xa0942deAc0885096D8400D3369dc4a2dde12875b'>, <Account object '0xf427a9eC1d510D77f4cEe4CF352545071387B2e6'>, <Account object '0x2308D528e4930EFB4aF30793A3F17295a0EFa886'>, <Account object '0x2fb37EB570B1eE8Eda736c1BD1E82748Ec3d0Bf1'>]
        >>> dir(accounts)
        [add, at, clear, load, remove]

.. py:classmethod:: Accounts.add(priv_key=None)

    Creates a new ``LocalAccount`` with private key ``priv_key``, appends it to the container, and returns the new account instance.  If no private key is entered, one is randomly generated via ``os.urandom(8192)``.

    .. code-block:: python

        >>> accounts.add()
        <Account object '0xb094716BC0E9D3F3Fb42FF928bd76618435FeeAA'>
        >>> accounts.add('8fa2fdfb89003176a16b707fc860d0881da0d1d8248af210df12d37860996fb2')
        <Account object '0xc1826925377b4103cC92DeeCDF6F96A03142F37a'>

.. py:classmethod:: Accounts.at(address)

    Given an address as a string, returns the corresponding ``Account`` or ``LocalAccount`` from the container.

    .. code-block:: python

        >>> accounts.at('0xc1826925377b4103cC92DeeCDF6F96A03142F37a')
        <Account object '0xc1826925377b4103cC92DeeCDF6F96A03142F37a'>

.. py:classmethod:: Accounts.clear()

    Empties the container.

    .. code-block:: python

        >>> accounts.clear()
        >>>

.. py:classmethod:: Accounts.load(filename=None)

    Loads a local account from a keystore file. If filename is ``None``, returns a list of available keystores.

    .. code-block:: python

        >>> accounts.load()
        ['my_account']
        >>> accounts.load('my_account')
        Enter the password for this account:
        <LocalAccount object '0xa9c2DD830DfFE8934fEb0A93BAbcb6e823e1FF05'>

.. py:classmethod:: Accounts.remove(address)

    Removes an address from the container. The address may be given as a string or an ``Account`` instance.

    .. code-block:: python

        >>> accounts.remove('0xc1826925377b4103cC92DeeCDF6F96A03142F37a')
        >>>

Account
-------

.. py:class:: brownie.network.accounts.Account

    An ethereum address that you control the private key for, and so can send transactions from. Generated automatically from ``web3.eth.accounts`` and stored in the ``Accounts`` container.

    .. code-block:: python

        >>> accounts[0]
        <Account object '0x7Ebaa12c5d1EE7fD498b51d4F9278DC45f8D627A'>
        >>> dir(accounts[0])
        [address, balance, deploy, estimate_gas, nonce, transfer]

Account Attributes
******************

.. py:attribute:: Account.address

    The public address of the account. Viewable by printing the class, you do not need to call this attribute directly.

    .. code-block:: python

        >>> accounts[0].address
        '0x7Ebaa12c5d1EE7fD498b51d4F9278DC45f8D627A'

.. py:attribute:: Account.nonce

    The current nonce of the address.

    .. code-block:: python

        >>> accounts[0].nonce
        0

Account Methods
***************

.. py:classmethod:: Account.balance()

    Returns the current balance at the address, in wei as an integer.

    .. code-block:: python

        >>> accounts[0].balance()
        100000000000000000000

.. py:classmethod:: Account.deploy(contract, *args)

    Deploys a contract.

    * ``contract``: A ``ContractContainer`` instance of the contract to be deployed.
    * ``*args``: Contract constructor arguments.

    You can optionally include a dictionary of `transaction parameters <https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.sendTransaction>`__ as the final argument.

    Returns a ``Contract`` instance upon success. If the transaction reverts or you do not wait for a confirmation, a ``TransactionReceipt`` is returned instead.

    .. code-block:: python

        >>> Token
        []
        >>> t = accounts[0].deploy(Token, "Test Token", "TST", 18, "1000 ether")

        Transaction sent: 0x2e3cab83342edda14141714ced002e1326ecd8cded4cd0cf14b2f037b690b976
        Transaction confirmed - block: 1   gas spent: 594186
        Contract deployed at: 0x5419710735c2D6c3e4db8F30EF2d361F70a4b380
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>
        >>>
        >>> t
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>
        >>> Token
        [<Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>]
        >>> Token[0]
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>

.. py:classmethod:: Account.estimate_gas(to, amount, data="")

    Estimates the gas required to perform a transaction. Raises a ``VirtualMachineError`` if the transaction would revert.

    * ``to``: Recipient address. Can be an ``Account`` instance or string.
    * ``amount``: Amount to send, in wei_.
    * ``data``: Transaction data hexstring.

    .. code-block:: python

        >>> accounts[0].estimate_gas(accounts[1], "1 ether")
        21000

.. py:classmethod:: Account.transfer(self, to, amount, gas_limit=None, gas_price=None, data="")

    Broadcasts a transaction from this account.

    * ``to``: Recipient address. Can be an ``Account`` instance or string.
    * ``amount``: Amount to send, in wei_.
    * ``gas_limit``: Gas limit, in wei_. If none is given, the price is set using ``eth_estimateGas``.
    * ``gas_price``: Gas price, in wei_. If none is given, the price is set using ``eth_gasPrice``.
    * ``data``: Transaction data hexstring.

    Returns a ``TransactionReceipt`` instance.

    .. code-block:: python

        >>> accounts[0].transfer(accounts[1], "1 ether")

        Transaction sent: 0x0173aa6938c3a5e50b6dc7b4d38e16dab40811ab4e00e55f3e0d8be8491c7852
        Transaction confirmed - block: 1   gas used: 21000 (100.00%)
        <Transaction object '0x0173aa6938c3a5e50b6dc7b4d38e16dab40811ab4e00e55f3e0d8be8491c7852'>

LocalAccount
------------

.. py:class:: brownie.network.accounts.LocalAccount

    Functionally identical to ``Account``. The only difference is that a ``LocalAccount`` is one where the private key was directly inputted, and so is not found in ``web3.eth.accounts``.

    >>> accounts.add()
    <LocalAccount object '0x716E8419F2926d6AcE07442675F476ace972C580'>
    >>> accounts[-1]
    <LocalAccount object '0x716E8419F2926d6AcE07442675F476ace972C580'>

.. py:attribute:: LocalAccount.public_key

    The local account's public key as a string.

    >>> accounts[-1].public_key
    '0x34b51e2913f5771acdddea7d353404f844b02a39ad4003c08afaa729993c43e890181327beaf352d81424cd277f4badc55be789a2817ea097bc82ea4801fee5b'

.. py:attribute:: LocalAccount.private_key

    The local account's private key as a string.

    >>> accounts[-1].private_key
    '0xd289bec8d9ad145aead13911b5bbf01936cbcd0efa0e26d5524b5ad54a61aeb8'

Contracts
=========

Contract classes are not meant to be instantiated directly. When launched, Brownie automatically creates ``ContractContainer`` instances from on the files in the ``contracts/`` folder. New ``Contract`` instances are created via methods in the container.

Arguments supplied to calls or transaction methods are converted using the methods outlined in :ref:`_type-conversions`.

ContractContainer
-----------------

.. py:class:: brownie.network.contract.ContractContainer

    A list-like container class that holds all ``Contract`` instances of the same type, and is used to deploy new instances of that contract.

    .. code-block:: python
        >>> Token
        []
        >>> dir(Token)
        [abi, at, bytecode, deploy, remove, signatures, topics, tx]

ContractContainer Attributes
****************************

.. py:attribute:: ContractContainer.abi

    The ABI of the contract.

    >>> Token.abi
    [{'constant': True, 'inputs': [], 'name': 'name', 'outputs': [{'name': '', 'type': 'string'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}], 'name': 'approve', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, ... ]

.. py:attribute:: ContractContainer.bytecode

    The bytecode of the contract, without any applied constructor arguments.

    >>> Token.bytecode
    '608060405234801561001057600080fd5b506040516107873803806107878339810160409081528151602080840151928401516060850151928501805190959490940193909291610055916000918701906100d0565b5082516100699060019060208601906100d0565b50600282905560038190553360008181526004602090815 ...

.. py:attribute:: ContractContainer.signatures

    A dictionary of bytes4 signatures for each contract method.

    If you have a signature and need to find the method name, use ``ContractContainer.get_method``.

    .. code-block:: python

        >>> Token.signatures
        {
            'allowance': "0xdd62ed3e",
            'approve': "0x095ea7b3",
            'balanceOf': "0x70a08231",
            'decimals': "0x313ce567",
            'name': "0x06fdde03",
            'symbol': "0x95d89b41",
            'totalSupply': "0x18160ddd",
            'transfer': "0xa9059cbb",
            'transferFrom': "0x23b872dd"
        }
        >>> Token.signatures.keys()
        dict_keys(['name', 'approve', 'totalSupply', 'transferFrom', 'decimals', 'balanceOf', 'symbol', 'transfer', 'allowance'])
        >>> Token.signatures['transfer']
        0xa9059cbb

.. py:attribute:: ContractContainer.topics

    A dictionary of bytes32 topics for each contract event.

    .. code-block:: python

        >>> Token.topics
        {
            'Approval': "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
            'Transfer': "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        }
        >>> Token.topics.keys()
        dict_keys(['Transfer', 'Approval'])
        >>> Token.topics['Transfer']
        0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef

ContractContainer Methods
*************************

.. py:classmethod:: ContractContainer.deploy(account, *args)

    Deploys the contract.

    * ``account``: An ``Account`` instance to deploy the contract from.
    * ``*args``: Contract constructor arguments.

    You can optionally include a dictionary of `transaction parameters <https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.sendTransaction>`__ as the final argument. If you omit this or do not specify a ``'from'`` value, the transaction will be sent from the same address that deployed the contract.

    If the contract requires a library, the most recently deployed one will be used. If the required library has not been deployed yet an ``IndexError`` is raised.

    Returns a ``Contract`` instance upon success.

    In the console if the transaction reverts or you do not wait for a confirmation, a ``TransactionReceipt`` is returned instead.

    .. code-block:: python

        >>> Token
        []
        >>> Token.deploy
        <ContractConstructor object 'Token.constructor(string,string,uint256,uint256)'>
        >>> t = Token.deploy(accounts[1], "Test Token", "TST", 18, "1000 ether")

        Transaction sent: 0x2e3cab83342edda14141714ced002e1326ecd8cded4cd0cf14b2f037b690b976
        Transaction confirmed - block: 1   gas spent: 594186
        Contract deployed at: 0x5419710735c2D6c3e4db8F30EF2d361F70a4b380
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>
        >>>
        >>> t
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>
        >>> Token
        [<Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>]
        >>> Token[0]
        <Token Contract object '0x5419710735c2D6c3e4db8F30EF2d361F70a4b380'>

.. py:classmethod:: ContractContainer.at(address, owner=None)

    Returns a ``Contract`` instance.

    * ``address``: Address where the contract is deployed. Raises a ValueError if there is no bytecode at the address.
    * ``owner``: ``Account`` instance to set as the contract owner. If transactions to the contract do not specify a ``'from'`` value, they will be sent from this account.

    .. code-block:: python

        >>> Token
        [<Token Contract object '0x79447c97b6543F6eFBC91613C655977806CB18b0'>]
        >>> Token.at('0x79447c97b6543F6eFBC91613C655977806CB18b0')
        <Token Contract object '0x79447c97b6543F6eFBC91613C655977806CB18b0'>
        >>> Token.at('0xefb1336a2E6B5dfD83D4f3a8F3D2f85b7bfb61DC')
        File "brownie/lib/console.py", line 82, in _run
            exec('_result = ' + cmd, self.__dict__, local_)
        File "<string>", line 1, in <module>
        File "brownie/lib/components/contract.py", line 121, in at
            raise ValueError("No contract deployed at {}".format(address))
        ValueError: No contract deployed at 0xefb1336a2E6B5dfD83D4f3a8F3D2f85b7bfb61DC


.. py:classmethod:: ContractContainer.remove(address)

    Removes a contract instance from the container.

    .. code-block:: python

        >>> Token
        [<Token Contract object '0x79447c97b6543F6eFBC91613C655977806CB18b0'>]
        >>> Token.remove('0x79447c97b6543F6eFBC91613C655977806CB18b0')
        >>> Token
        []

.. py:classmethod:: ContractContainer.get_method(calldata)

    Given the call data of a transaction, returns the name of the contract method as a string.

    .. code-block:: python

        >>> tx = Token[0].transfer(accounts[1], 1000)

        Transaction sent: 0xc1fe0c7c8fd08736718aa9106662a635102604ea6db4b63a319e43474de0b420
        Token.transfer confirmed - block: 3   gas used: 35985 (26.46%)
        <Transaction object '0xc1fe0c7c8fd08736718aa9106662a635102604ea6db4b63a319e43474de0b420'>
        >>> tx.input
        0xa9059cbb00000000000000000000000066ace0365c25329a407002d22908e25adeacb9bb00000000000000000000000000000000000000000000000000000000000003e8
        >>> Token.get_method(tx.input)
        transfer

Contract
--------

.. py:class:: brownie.network.contract.Contract

    A deployed contract. This class allows you to call or send transactions to the contract.

    .. code-block:: python

        >>> Token[0]
        <Token Contract object '0x79447c97b6543F6eFBC91613C655977806CB18b0'>
        >>> dir(Token[0])
        [abi, allowance, approve, balance, balanceOf, bytecode, decimals, name, signatures, symbol, topics, totalSupply, transfer, transferFrom, tx]

Contract Attributes
*******************

.. py:attribute:: Contract.bytecode

    The bytecode of the deployed contract, including constructor arguments.

    .. code-block:: python

        >>> Token[0].bytecode
        '6080604052600436106100985763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166306fdde03811461009d578063095ea7b31461012757806318160ddd1461015f57806323b872dd14610186578063313ce567146101b057806370a08231146101c557806395d89b41...

.. py:attribute:: Contract.tx

    The ``TransactionReceipt`` of the transaction that deployed the contract. If the contract was not deployed during this instance of brownie, it will be ``None``.

    .. code-block:: python

        >>> Token[0].tx
        <Transaction object '0xcede03c7e06d2b4878438b08cd0cf4515942b3ba06b3cfd7019681d18bb8902c'>

Contract Methods
****************

.. py:classmethod:: Contract.balance()

    Returns the balance at the contract address, in wei at an int.

    .. code-block:: python

        >>> Token[0].balance
        0

.. _api-contract-call:

ContractCall
------------

.. py:class:: brownie.network.contract.ContractCall(*args)

    Calls a non state-changing contract method without broadcasting a transaction, and returns the result. ``args`` must match the required inputs for the method.

    The expected inputs are shown in the method's ``__repr__`` value.

    .. code-block:: python

        >>> Token[0].allowance
        <ContractCall object 'allowance(address,address)'>
        >>> Token[0].allowance(accounts[0], accounts[2])
        0

ContractCall Attributes
***********************

.. py:attribute:: ContractCall.abi

    The contract ABI specific to this method.

    .. code-block:: python

        >>> Token[0].allowance.abi
        {
            'constant': True,
            'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}],
            'name': "allowance",
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': "view",
            'type': "function"
        }

.. py:attribute:: ContractCall.signature

    The bytes4 signature of this method.

    .. code-block:: python

        >>> Token[0].allowance.signature
        '0xdd62ed3e'

ContractCall Methods
********************

.. py:classmethod:: ContractCall.transact(*args)

    Sends a transaction to the method and returns a ``TransactionReceipt``.

    .. code-block:: python

        >>> tx = Token[0].allowance.transact(accounts[0], accounts[2])

        Transaction sent: 0xc4f3a0addfe1e475c2466f30c750ca7a60450132b07102af610d8d56f170046b
        Token.allowance confirmed - block: 2   gas used: 24972 (19.98%)
        <Transaction object '0xc4f3a0addfe1e475c2466f30c750ca7a60450132b07102af610d8d56f170046b'>
        >>> tx.return_value
        0

.. _api-contract-tx:

ContractTx
----------

.. py:class:: brownie.network.contract.ContractTx(*args)

    Sends a transaction to a potentially state-changing contract method. Returns a ``TransactionReceipt``.

    You can optionally include a dictionary of `transaction parameters <https://web3py.readthedocs.io/en/stable/web3.eth.html#web3.eth.Eth.sendTransaction>`__ as the final argument. If you omit this or do not specify a ``'from'`` value, the transaction will be sent from the same address that deployed the contract.

    .. code-block:: python

        >>> Token[0].transfer
        <ContractTx object 'transfer(address,uint256)'>
        >>> Token[0].transfer(accounts[1], 100000, {'from':accounts[0]})

        Transaction sent: 0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0
        Transaction confirmed - block: 2   gas spent: 51049
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>

ContractTx Attributes
*********************

.. py:attribute:: ContractTx.abi

    The contract ABI specific to this method.

    .. code-block:: python

        >>> Token[0].transfer.abi
        {
            'constant': False,
            'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': "transfer",
            'outputs': [{'name': '', 'type': 'bool'}],
            'payable': False,
            'stateMutability': "nonpayable",
            'type': "function"
        }

.. py:attribute:: ContractTx.signature

    The bytes4 signature of this method.

    .. code-block:: python

        >>> Token[0].transfer.signature
        '0xa9059cbb'

ContractTx Methods
******************

.. py:classmethod:: ContractTx.call(*args)

    Calls the contract method without broadcasting a transaction, and returns the result.

    .. code-block:: python

        >>> Token[0].transfer.call(accounts[2], 10000, {'from': accounts[0]})
        True

.. py:classmethod:: ContractTx.encode_abi(*args)

    Returns a hexstring of ABI calldata, to call the method with the given arguments.

    .. code-block:: python

        >>> calldata = Token[0].transfer.encode_abi(accounts[1], 1000)
        0xa9059cbb0000000000000000000000000d36bdba474b5b442310a5bfb989903020249bba00000000000000000000000000000000000000000000000000000000000003e8
        >>> accounts[0].transfer(Token[0], 0, data=calldata)

        Transaction sent: 0x8dbf15878104571669f9843c18afc40529305ddb842f94522094454dcde22186
        Token.transfer confirmed - block: 2   gas used: 50985 (100.00%)
        <Transaction object '0x8dbf15878104571669f9843c18afc40529305ddb842f94522094454dcde22186'>

Event
=====


History
=======


.. _rpc:

RPC
===

.. py:class:: brownie.network.rpc.Rpc

    Exposes methods for interacting with ``ganache-cli`` when running a local RPC environment. When using the console or writing tests, an instance of this class is available as ``rpc``.

    .. code-block:: python

        >>> rpc
        <lib.components.eth.Rpc object at 0x7ffb7cbab048>
        >>> dir(rpc)
        [mine, revert, sleep, snapshot, time]

.. py:classmethod:: Rpc.time()

    Returns the current epoch time in the RPC as an integer.

    .. code-block:: python

        >>> rpc.time()
        1550189043

.. py:classmethod:: Rpc.sleep(seconds)

    Advances the RPC time. You can only advance the time by whole seconds.

    .. code-block:: python

        >>> rpc.time()
        1550189043
        >>> rpc.sleep(100)
        >>> rpc.time()
        1550189145

.. py:classmethod:: Rpc.mine(blocks = 1)

    Forces new blocks to be mined.

    .. code-block:: python

        >>> web3.eth.blockNumber
        0
        >>> rpc.mine()
        Block height at 1
        >>> web3.eth.blockNumber
        1
        >>> rpc.mine(3)
        Block height at 4
        >>> web3.eth.blockNumber
        4

.. py:classmethod:: Rpc.snapshot()

    Creates a snapshot at the current block height.

    .. code-block:: python

        >>> rpc.snapshot()
        Snapshot taken at block height 4

.. py:classmethod:: Rpc.revert()

    Reverts the blockchain to the latest snapshot. Raises ``ValueError`` if no snapshot has been taken.

    .. code-block:: python

        >>> rpc.snapshot()
        Snapshot taken at block height 4
        >>> accounts[0].balance()
        100000000000000000000
        >>> accounts[0].transfer(accounts[1], "10 ether")

        Transaction sent: 0xd5d3b40eb298dfc48721807935eda48d03916a3f48b51f20bcded372113e1dca
        Transaction confirmed - block: 5   gas used: 21000 (100.00%)
        <Transaction object '0xd5d3b40eb298dfc48721807935eda48d03916a3f48b51f20bcded372113e1dca'>
        >>> accounts[0].balance()
        89999580000000000000
        >>> rpc.revert()
        Block height reverted to 4
        >>> accounts[0].balance()
        100000000000000000000


Transactions
============

.. _api-network-tx:

TransactionReceipt
------------------

.. py:class:: brownie.network.transaction.TransactionReceipt

    An instance of this class is returned whenever a transaction is broadcasted. When printed in the console, they will it yellow if the transaction is still pending or red if the transaction caused the EVM to revert.

    Many of the attributes will be set to ``None`` while the transaction is still pending.

    .. code-block:: python

        >>> tx = Token[0].transfer
        <ContractTx object 'transfer(address,uint256)'>
        >>> Token[0].transfer(accounts[1], 100000, {'from':accounts[0]})

        Transaction sent: 0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0
        Transaction confirmed - block: 2   gas spent: 51049
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> dir(tx)
        [block_number, call_trace, contract_address, error, events, fn_name, gas_limit, gas_price, gas_used, info, input, logs, nonce, receiver, sender, status, txid, txindex, value]

TransactionReceipt Attributes
*****************************

.. py:attribute:: TransactionReceipt.block_number

    The block height at which the transaction confirmed.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.block_number
        2

.. py:attribute:: TransactionReceipt.contract_address

    The address of the contract deployed as a result of this transaction, if any.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.contract_address
        None

.. py:attribute:: TransactionReceipt.events

    A dictionary of decoded event logs for this transaction. If you are connected to an RPC client that allows for ``debug_traceTransaction``, event data is still available when the transaction reverts.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.events
        [{'name': 'Transfer', 'data': [{'name': 'from', 'type': 'address', 'value': '0x6b5132740b834674c3277aafa2c27898cbe740f6', 'decoded': True}, {'name': 'to', 'type': 'address', 'value': '0x31d504908351d2d87f3d6111f491f0b52757b592', 'decoded': True}, {'name': 'value', 'type': 'uint256', 'value': 1000000, 'decoded': True}]}]

.. py:attribute:: TransactionReceipt.fn_name

    The name of the contract and function called by the transaction.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.fn_name
        'Token.transfer'

.. py:attribute:: TransactionReceipt.gas_limit

    The gas limit of the transaction, in wei as an int.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.gas_limit
        150921

.. py:attribute:: TransactionReceipt.gas_price

    The gas price of the transaction, in wei as an int.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.gas_price
        2000000000

.. py:attribute:: TransactionReceipt.gas_used

    The amount of gas consumed by the transaction, in wei as an int.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.gas_used
        51049

.. py:attribute:: TransactionReceipt.input

    The complete calldata of the transaction.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.input
        '0xa9059cbb00000000000000000000000031d504908351d2d87f3d6111f491f0b52757b592000000000000000000000000000000000000000000000000000000000000000a'


.. py:attribute:: TransactionReceipt.logs

    The raw event logs for the transaction. Not available if the transaction reverts.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.logs
        [AttributeDict({'logIndex': 0, 'transactionIndex': 0, 'transactionHash': HexBytes('0xa8afb59a850adff32548c65041ec253eb64e1154042b2e01e2cd8cddb02eb94f'), 'blockHash': HexBytes('0x0b93b4cf230c9ef92b990de9cd62611447d83d396f1b13204d26d28bd949543a'), 'blockNumber': 6, 'address': '0x79447c97b6543F6eFBC91613C655977806CB18b0', 'data': '0x0000000000000000000000006b5132740b834674c3277aafa2c27898cbe740f600000000000000000000000031d504908351d2d87f3d6111f491f0b52757b592000000000000000000000000000000000000000000000000000000000000000a', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')], 'type': 'mined'})]

.. py:attribute:: TransactionReceipt.nonce

    The nonce of the transaction.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.nonce
        2

.. py:attribute:: TransactionReceipt.receiver

    The address the transaction was sent to, as a string.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.receiver
        '0x79447c97b6543F6eFBC91613C655977806CB18b0'

.. py:attribute:: TransactionReceipt.revert_msg

    The error string returned when a transaction causes the EVM to revert, if any.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.revert_msg
        None

.. py:attribute:: TransactionReceipt.return_value

    The value returned from the called function, if any. Only available if the RPC client allows ``debug_traceTransaction``.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.return_value
        True

.. py:attribute:: TransactionReceipt.sender

    The address the transaction was sent from. Where possible, this will be an Account instance instead of a string.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.sender
        <Account object '0x6B5132740b834674C3277aAfa2C27898CbE740f6'>

.. py:attribute:: TransactionReceipt.status

    The status of the transaction: -1 for pending, 0 for failed, 1 for success.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.status
        1

.. py:attribute:: TransactionReceipt.trace

    The structLog from the `debug_traceTransaction <https://github.com/ethereum/go-ethereum/wiki/Management-APIs#debug_tracetransaction>`__ RPC method. If you are using Infura this attribute is not available.

    Along with the standard data, the structLog also contains the following additional information:

    * ``address``: The address of the contract that executed this opcode
    * ``contractName``: The name of the contract
    * ``fn``: The name of the function
    * ``jumpDepth``: The number of jumps made since entering this contract. The initial function has a value of 1.
    * ``source``: The start and end offset of the source code associated with this opcode.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> len(tx.trace)
        239
        >>> tx.trace[0]
        {
            'address': "0x79447c97b6543F6eFBC91613C655977806CB18b0",
            'contractName': "Token",
            'depth': 0,
            'error': "",
            'fn': "transfer",
            'gas': 128049,
            'gasCost': 22872,
            'jumpDepth': 1,
            'memory': [],
            'op': "PUSH1",
            'pc': 0,
            'source': {
                'filename': "contracts/Token.sol",
                'start': 53,
                'stop': 2053
            },
            'stack': [],
            'storage': {
            }
        }

.. py:attribute:: TransactionReceipt.txid

    The transaction hash.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.txid
        '0xa8afb59a850adff32548c65041ec253eb64e1154042b2e01e2cd8cddb02eb94f'

.. py:attribute:: TransactionReceipt.txindex

    The integer of the transaction's index position in the block.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.txindex
        0

.. py:attribute:: TransactionReceipt.value

    The value of the transaction, in wei as an int.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.value
        0

TransactionReceipt Methods
**************************

.. py:classmethod:: TransactionReceipt.info()

    Displays verbose information about the transaction, including event logs and the error string if a transaction reverts.

    .. code-block:: python

        >>> tx = accounts[0].transfer(accounts[1], 100)
        <Transaction object '0x2facf2d1d2fdfa10956b7beb89cedbbe1ba9f4a2f0592f8a949d6c0318ec8f66'>
        >>> tx.info()

        Transaction was Mined
        ---------------------
        Tx Hash: 0x2facf2d1d2fdfa10956b7beb89cedbbe1ba9f4a2f0592f8a949d6c0318ec8f66
        From: 0x5fe657e72E76E7ACf73EBa6FA07ecB40b7312d80
        To: 0x5814fC82d51732c412617Dfaecb9c05e3B823253
        Value: 100
        Block: 1
        Gas Used: 21000

           Events In This Transaction
           --------------------------
           Transfer
              from: 0x5fe657e72E76E7ACf73EBa6FA07ecB40b7312d80
              to: 0x31d504908351d2d87f3d6111f491f0b52757b592
              value: 100

.. py:classmethod:: TransactionReceipt.call_trace()

    Displays the sequence of contracts and functions called while executing this transaction, and the structLog index where each call or jump occured. Any functions that terminated with ``REVERT`` or ``INVALID`` opcodes are highlighted in red.

    .. code-block:: python

        >>> tx = Token[0].transferFrom(accounts[2], accounts[3], "10000 ether")

        Transaction sent: 0x0d96e8ceb555616fca79dd9d07971a9148295777bb767f9aa5b34ede483c9753
        Token.transferFrom confirmed (reverted) - block: 4   gas used: 25425 (26.42%)

        >>> tx.call_trace()
        Token.transferFrom 0 (0x4C2588c6BFD533E0a27bF7572538ca509f31882F)
          Token.sub 86 (0x4C2588c6BFD533E0a27bF7572538ca509f31882F)

.. py:classmethod:: TransactionReceipt.error(pad=3)

    Displays the source code that caused the first revert in the transaction, if any.

    * ``pad``: Number of unrelated lines to show around the relevent source code.

    .. code-block:: python

        >>> tx
        <Transaction object '0xac54b49987a77805bf6bdd78fb4211b3dc3d283ff0144c231a905afa75a06db0'>
        >>> tx.error()
        File "contracts/SafeMath.sol", line 9:

                c = a + b;
                require(c >= a);
            }
            function sub(uint a, uint b) internal pure returns (uint c) {
                require(b <= a);
                c = a - b;
            }
            function mul(uint a, uint b) internal pure returns (uint c) {
                c = a * b;

Web3
====

.. py:attribute:: brownie.network.web3