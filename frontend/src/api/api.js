const BASE_URL = "http://localhost:5000";

export const fetchDisasterInfo = async (location) => {
    const response = await fetch(`${BASE_URL}/get-disaster-info`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(location),
    });
    return response.json();
};

export const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
        console.log("Uploading image...");

        const response = await fetch(`${BASE_URL}/upload-image`, {
            method: "POST",
            body: formData,
        });

        console.log("Response status:", response.status);

        // Parse JSON response
        const result = await response.json();
        console.log("Response data:", result);

        if (response.ok && result.success) {
            console.log("Image received successfully:", result.message);
            return result;
        } else {
            console.error("Failed to upload image:", result.message || "Unknown error");
            return { success: false, message: result.message || "Unknown error occurred" };
        }
    } catch (error) {
        console.error("Error uploading image:", error);
        return { success: false, message: "An error occurred while uploading the image" };
    }
};


export const sendMessage = async (message) => {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
    });
    return response.json();
};
