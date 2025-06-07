 document.addEventListener('DOMContentLoaded', function() {
    const feedbackButton = document.getElementById('feedback-button');
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedback = document.getElementById('close-feedback');
    const submitFeedback = document.getElementById('submit-feedback');
    const feedbackSuccess = document.getElementById('feedback-success');
    const ratingStars = document.querySelectorAll('.rating-star');
    const feedbackTypes = document.querySelectorAll('.feedback-type');

    let selectedRating = 0;
    let selectedType = '';

    // Toggle feedback modal
    feedbackButton.addEventListener('click', function() {
      feedbackModal.classList.remove('hidden');
      feedbackModal.querySelector('.animate__fadeInUp').classList.add('animate__fadeInUp');
    });

    closeFeedback.addEventListener('click', function() {
      feedbackModal.classList.add('hidden');
    });

    // Rating stars
    ratingStars.forEach(star => {
      star.addEventListener('click', function() {
        const rating = parseInt(this.getAttribute('data-rating'));
        selectedRating = rating;

        // Update stars display
        ratingStars.forEach((s, index) => {
          if (index < rating) {
            s.innerHTML = '<i class="fas fa-star text-yellow-400 text-xl"></i>';
            s.classList.add('bg-yellow-50');
            s.classList.remove('bg-gray-100');
          } else {
            s.innerHTML = '<i class="far fa-star text-gray-400 text-xl"></i>';
            s.classList.add('bg-gray-100');
            s.classList.remove('bg-yellow-50');
          }
        });
      });
    });

    // Feedback types
    feedbackTypes.forEach(type => {
      type.addEventListener('click', function() {
        feedbackTypes.forEach(t => t.classList.remove('bg-blue-50', 'bg-green-50', 'bg-purple-50', 'bg-red-50', 'border-primary'));
        this.classList.add(this.classList.contains('hover:bg-blue-50') ? 'bg-blue-50' :
                          this.classList.contains('hover:bg-green-50') ? 'bg-green-50' :
                          this.classList.contains('hover:bg-purple-50') ? 'bg-purple-50' : 'bg-red-50');
        this.classList.add('border-primary');
        selectedType = this.getAttribute('data-type');
      });
    });

    // Submit feedback
    submitFeedback.addEventListener('click', function() {
      const message = document.getElementById('feedback-message').value;

      // Here you would typically send the data to your backend
      console.log('Feedback submitted:', {
        rating: selectedRating,
        type: selectedType,
        message: message
      });

      // Show success message
      feedbackModal.classList.add('hidden');
      feedbackSuccess.classList.remove('hidden');
      feedbackSuccess.querySelector('.animate__fadeInUp').classList.add('animate__fadeInUp');

      // Hide after 3 seconds
      setTimeout(() => {
        feedbackSuccess.classList.add('hidden');
      }, 3000);

      // Reset form
      selectedRating = 0;
      selectedType = '';
      document.getElementById('feedback-message').value = '';
      ratingStars.forEach(star => {
        star.innerHTML = '<i class="far fa-star text-gray-400 text-xl"></i>';
        star.classList.add('bg-gray-100');
        star.classList.remove('bg-yellow-50');
      });
      feedbackTypes.forEach(type => {
        type.classList.remove('bg-blue-50', 'bg-green-50', 'bg-purple-50', 'bg-red-50', 'border-primary');
      });
    });
    document.getElementById('close-feedback').addEventListener('click', function() {
      document.getElementById('feedback-modal').classList.add('hidden');
    });

    document.getElementById('close-success').addEventListener('click', function() {
      document.getElementById('feedback-success').classList.add('hidden');
    });
  });