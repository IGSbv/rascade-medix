const Web3 = require('web3');
const solc = require('solc');
const fs = require('fs');

// Connect to local Ethereum node (Ganache)
const web3 = new Web3(new Web3.providers.HttpProvider('http://127.0.0.1:8545'));

// Ensure connection is successful
if (!web3.currentProvider.connected) {
    console.log("Failed to connect to the network.");
} else {
    console.log("Connected to Ethereum node.");
}

// Set default account
web3.eth.getAccounts().then(accounts => {
    web3.eth.defaultAccount = accounts[0];
    console.log("Default account:", web3.eth.defaultAccount);

    // Read contract source code
    const contractSourceCode = fs.readFileSync('./contracts/MedicalRecords.sol', 'utf8');

    // Compile Solidity code
    const input = {
        language: 'Solidity',
        sources: {
            'MedicalRecords.sol': {
                content: contractSourceCode,
            },
        },
        settings: {
            outputSelection: {
                '*': {
                    '*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap'],
                },
            },
        },
    };

    const compiledSol = JSON.parse(solc.compile(JSON.stringify(input)));
    const abi = compiledSol.contracts['MedicalRecords.sol'].MedicalRecords.abi;
    const bytecode = compiledSol.contracts['MedicalRecords.sol'].MedicalRecords.evm.bytecode.object;

    // Deploy contract
    const MedicalRecords = new web3.eth.Contract(abi);

    MedicalRecords.deploy({
        data: bytecode,
    })
        .send({
            from: web3.eth.defaultAccount,
            gas: 1500000,
            gasPrice: '30000000000',
        })
        .on('receipt', receipt => {
            console.log("Contract deployed at:", receipt.contractAddress);
        })
        .on('error', error => {
            console.error("Transaction failed:", error);
        });
});
