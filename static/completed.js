document.addEventListener('DOMContentLoaded', () => {
        const contentHolder = document.getElementById('contentHolder');
        const data = outputData();
        function loadAllData(){
            contentHolder.innerHTML="";
            for(let i =0 ;i<data.length;i++){
            contentHolder.innerHTML+=`<div class="contentBox">
                <div class="title">
                    <h3>${data[i][1]}</h3>
                    <h3>-${data[i][2]}</h3>
                </div>
                <div class="progressBar">
                    <div class="progress" style="width:${100}%;"></div>
                </div>
                <div class="peopleDetails">
                    <div class="assignedBy">Assigned By: ${data[i][3]}</div>
                </div>
                <div class="extraContent">
                    <hr>
                    <div>
                        <div class="taskDetails">
                            <p>Task Description: ${data[i][4]}</p>
                            <p>Progress: Finished</p>
                        </div>
                    </div>
                    <div class="ButtonHolder">
                            <button type="button" class="deleteButton" onclick="deleteData(${i},${data[i][0]})">Delete</button>
                    </div>
                </div>
            </div>`
            


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
