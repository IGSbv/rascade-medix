
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalRecords {
    struct Patient {
        string name;
        uint age;
        string symptoms;
        string medicalHistory;
    }
    
    struct Doctor {
        string name;
        string specialization;
        address[] patients;
    }

    mapping(address => Patient) public patients;
    mapping(address => Doctor) public doctors;
    mapping(address => bool) public isDoctor;

    // Register a patient
    function addPatient(
        string memory _name,
        uint _age,
        string memory _symptoms,
        string memory _medicalHistory
    ) public {
        patients[msg.sender] = Patient(_name, _age, _symptoms, _medicalHistory);
    }

    // Register a doctor
    function addDoctor(
        string memory _name,
        string memory _specialization
    ) public {
        require(!isDoctor[msg.sender], "Already a doctor");
        doctors[msg.sender] = Doctor(_name, _specialization, new address[](0)); // Initialize the Doctor struct properly
        isDoctor[msg.sender] = true;
    }

    // Link patient to doctor
    function assignPatientToDoctor(address patientAddress) public {
        require(isDoctor[msg.sender], "Only doctors can assign patients");
        doctors[msg.sender].patients.push(patientAddress);
    }

    // Retrieve patient's data
    function getPatient(address patientAddress) public view returns (Patient memory) {
        return patients[patientAddress];
    }

    // Retrieve doctor's patients
    function getDoctorPatients() public view returns (address[] memory) {
        require(isDoctor[msg.sender], "Only doctors can access this");
        return doctors[msg.sender].patients;
    }
}
