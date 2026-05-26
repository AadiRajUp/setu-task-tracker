document.addEventListener('DOMContentLoaded', () => {
        const contentHolder = document.getElementById('contentHolder');
        const data = outputData();
        localStorage.setItem("Data",JSON.stringify(data));
        console.log(data);
        username = getUsername();
        function loadAllData(){
            contentHolder.innerHTML="";
            for (let i = 0; i < data.length; i++) {

                let buttons = "";

                if (data[i][2] === username) {
                    buttons += `
                        <button type="button" class="editButton" id="editButton${data[i][0]}" onclick="editData(${i},${data[i][0]})">Edit</button>
                        `;
                    }
                
                if(data[i][3] === username || username === "admin"){
                    buttons += `                        
                    <button type="button" class="deleteButton" id="deleteButton${data[i][0]}" onclick="deleteData(${i},${data[i][0]})">Delete</button>
                        <button type="button" class="finishButton" id="finishButton${data[i][0]}" onclick="finishData(${i},${data[i][0]})">Finished</button>`;
                }

                contentHolder.innerHTML += `
                        <div class="contentBox">
                            <div class="title">
                                <h3>${data[i][1]}</h3>
                                <h3>-${data[i][2]}</h3>
                            </div>
                            <div class="progressBar">
                                <div class="progress" style="width:${data[i][8]}%;"></div>
                            </div>
                            <div class="numericData">
                                <h6>${data[i][4]}</h6>
                                <h6>${data[i][7]}</h6>
                            </div>
                            <div class="extraContent">
                                <hr>
                                <div>
                                    <div class="taskDetails">
                                        <p>Task Description: ${data[i][5]}</p>
                                        <p>Progress: ${data[i][6]}</p>
                                        <p>Remaining: ${data[i][7]}</p>
                                    </div>
                                    <div class="peopleDetails">
                                        <div class="peopleWorking">People Working: ${data[i][9]}</div>
                                        <div class="assignedBy">Assigned By: ${data[i][3]}</div>
                                    </div>
                                </div>
                                <div class="ButtonHolder">
                                    ${buttons}     
                                </div>
                            </div>
                        </div>
                    `;
            


            // Add click event listener to the newly created content box
            addToggleEventListeners();
            }
        }
        
        // Function to add toggle event listeners to all content boxes
        function addToggleEventListeners() {
            const contentBoxes = document.querySelectorAll('.contentBox');
            contentBoxes.forEach(box => {
                box.removeEventListener('click', toggleExtraContent);
                box.addEventListener('click', toggleExtraContent);
            });
        }
        
        // Function to toggle extra content visibility
        function toggleExtraContent(event) {
            const extraContent = this.querySelector('.extraContent');
            if (extraContent) {
                if (extraContent.style.display === 'none' || extraContent.style.display === '') {
                    extraContent.style.display = 'block';
                } else {
                    extraContent.style.display = 'none';
                }
            }
        }
        
        // Initialize event listeners for any existing content boxes
        loadAllData();
        addToggleEventListeners();
        
    }); 
