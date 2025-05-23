// Open the popup when the "Add to Collection" button is clicked
function openAddToCollectionPopup(button) {
    let itemId = button.getAttribute("data-item-id");
    document.getElementById("popupItemId").value = itemId;
    document.getElementById("collectionPopup").style.display = "flex"; // Show the popup
}

// Close the popup when the close button is clicked
function closePopup() {
    document.getElementById("collectionPopup").style.display = "none"; // Hide the popup
}

// Handle form submission to add the item to a collection
document.getElementById("collectionForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let formData = new FormData(this);
    
    fetch('/addToCollection/', {  // Ensure this URL matches your Django path
        method: 'POST',
        body: formData,
        headers: { "X-CSRFToken": csrfToken }  // Ensure csrfToken is passed if needed
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closePopup();  // Close the popup on success
        } else {
            alert("Error adding item.");
        }
    })
    .catch(error => console.error("Error:", error));
});

// window.addEventListener('load', function () {
//     console.log("HELLOOOOO");
//     const button = document.querySelector('.add-to-collection-btn');
//     console.log(button);
//     document.querySelectorAll('.add-to-collection-btn').forEach(button => {
//         button.addEventListener('click', function () {
//             const itemId = this.dataset.itemId;
//             fetch(`/cla/addToCollection/${itemId}/`, {
//                 headers: { 'X-Requested-With': 'XMLHttpRequest' }
//             })
//             .then(response => response.text())
//             .then(html => {
//                 const modalBody = document.getElementById('collectionModalBody');
//                 modalBody.innerHTML = html;
//                 const modal = new bootstrap.Modal(document.getElementById('collectionModal'));
//                 modal.show();
//             });
//         });
//     });
// });
