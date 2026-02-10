package com.example.gestionstationskii.contextSpring;

import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.entities.Instructor;
import com.example.gestionstationskii.repositories.ICourseRepository;
import com.example.gestionstationskii.repositories.IInstructorRepository;
import com.example.gestionstationskii.services.InstructorServicesImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Transactional  // rolls back after each test
class InstructorServicesImplTest {

    @Autowired
    private IInstructorRepository instructorRepository;

    @Autowired
    private ICourseRepository courseRepository;

    @Autowired
    private InstructorServicesImpl instructorServices;

    private Instructor instructor;
    private Course course;

    @BeforeEach
    void setUp() {
        // Clean database before each test
        instructorRepository.deleteAll();
        courseRepository.deleteAll();

        instructor = new Instructor();
        instructor.setFirstName("John");
        instructor.setLastName("Doe");
        instructor.setDateOfHire(LocalDate.of(2022, 1, 1));

        course = new Course();
        course.setLevel(1);
        course.setPrice(120.0f);
        course.setTimeSlot(3);

        // Save course first (needed for assignment)
        courseRepository.save(course);
    }

    @Test
    void testAddInstructor() {
        Instructor saved = instructorServices.addInstructor(instructor);

        assertThat(saved.getNumInstructor()).isNotNull();
        assertThat(saved.getFirstName()).isEqualTo("John");
        assertThat(instructorRepository.findAll()).hasSize(1);
    }

    @Test
    void testRetrieveAllInstructors() {
        instructorServices.addInstructor(instructor);

        List<Instructor> all = instructorServices.retrieveAllInstructors();
        assertThat(all).hasSize(1);
        assertThat(all.get(0).getLastName()).isEqualTo("Doe");
    }

    @Test
    void testUpdateInstructor() {
        Instructor saved = instructorServices.addInstructor(instructor);
        saved.setLastName("Smith");

        Instructor updated = instructorServices.updateInstructor(saved);

        assertThat(updated.getLastName()).isEqualTo("Smith");
    }

    @Test
    void testRetrieveInstructor_Found() {
        Instructor saved = instructorServices.addInstructor(instructor);

        Instructor found = instructorServices.retrieveInstructor(saved.getNumInstructor());
        assertThat(found).isNotNull();
        assertThat(found.getFirstName()).isEqualTo("John");
    }

    @Test
    void testRetrieveInstructor_NotFound() {
        Instructor found = instructorServices.retrieveInstructor(999L);
        assertThat(found).isNull();
    }

    @Test
    void testAddInstructorAndAssignToCourse_CourseFound() {
        Instructor saved = instructorServices.addInstructorAndAssignToCourse(instructor, course.getNumCourse());

        assertThat(saved).isNotNull();
        assertThat(saved.getCourses()).isNotEmpty();
        assertThat(saved.getCourses().iterator().next().getNumCourse()).isEqualTo(course.getNumCourse());
    }

    @Test
    void testAddInstructorAndAssignToCourse_CourseNotFound() {
        Instructor saved = instructorServices.addInstructorAndAssignToCourse(instructor, 999L);

        assertThat(saved).isNull();
    }
}
