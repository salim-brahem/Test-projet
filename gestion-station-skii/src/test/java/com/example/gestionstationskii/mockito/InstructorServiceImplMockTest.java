package com.example.gestionstationskii.mockito;

import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.entities.Instructor;
import com.example.gestionstationskii.repositories.ICourseRepository;
import com.example.gestionstationskii.repositories.IInstructorRepository;
import com.example.gestionstationskii.services.InstructorServicesImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.*;

import java.time.LocalDate;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class InstructorServiceImplMockTest {

    @Mock
    private IInstructorRepository instructorRepository;

    @Mock
    private ICourseRepository courseRepository;

    @InjectMocks
    private InstructorServicesImpl instructorServices;

    private Instructor instructor;
    private Course course;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        instructor = new Instructor();
        instructor.setNumInstructor(1L);
        instructor.setFirstName("Alice");
        instructor.setLastName("Smith");
        instructor.setDateOfHire(LocalDate.of(2023, 5, 15));

        course = new Course();
        course.setNumCourse(200L);
        course.setLevel(2);
        course.setTypeCourse(null);
        course.setSupport(null);
        course.setPrice(150.0f);
        course.setTimeSlot(4);
    }

    @Test
    @DisplayName("Add Instructor - should save and return instructor")
    void addInstructorTest() {
        when(instructorRepository.save(any(Instructor.class))).thenReturn(instructor);

        Instructor saved = instructorServices.addInstructor(instructor);

        assertThat(saved).isNotNull();
        assertThat(saved.getFirstName()).isEqualTo("Alice");
        verify(instructorRepository, times(1)).save(instructor);
    }

    @Test
    @DisplayName("Retrieve all instructors - should return list")
    void retrieveAllInstructorsTest() {
        List<Instructor> instructors = List.of(instructor);
        when(instructorRepository.findAll()).thenReturn(instructors);

        List<Instructor> result = instructorServices.retrieveAllInstructors();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getLastName()).isEqualTo("Smith");
        verify(instructorRepository, times(1)).findAll();
    }

    @Test
    @DisplayName("Update Instructor - should save and return updated instructor")
    void updateInstructorTest() {
        when(instructorRepository.save(any(Instructor.class))).thenReturn(instructor);

        Instructor updated = instructorServices.updateInstructor(instructor);

        assertThat(updated).isNotNull();
        assertThat(updated.getNumInstructor()).isEqualTo(1L);
        verify(instructorRepository, times(1)).save(instructor);
    }

    @Test
    @DisplayName("Retrieve Instructor by ID - found")
    void retrieveInstructorFoundTest() {
        when(instructorRepository.findById(1L)).thenReturn(Optional.of(instructor));

        Instructor found = instructorServices.retrieveInstructor(1L);

        assertThat(found).isNotNull();
        assertThat(found.getFirstName()).isEqualTo("Alice");
        verify(instructorRepository, times(1)).findById(1L);
    }

    @Test
    @DisplayName("Retrieve Instructor by ID - not found")
    void retrieveInstructorNotFoundTest() {
        when(instructorRepository.findById(999L)).thenReturn(Optional.empty());

        Instructor result = instructorServices.retrieveInstructor(999L);

        assertThat(result).isNull();
        verify(instructorRepository, times(1)).findById(999L);
    }

    @Test
    @DisplayName("Add Instructor and assign to Course - course exists")
    void addInstructorAndAssignToCourseFoundTest() {
        when(courseRepository.findById(200L)).thenReturn(Optional.of(course));
        when(instructorRepository.save(any(Instructor.class))).thenReturn(instructor);

        Instructor result = instructorServices.addInstructorAndAssignToCourse(instructor, 200L);

        assertThat(result).isNotNull();
        assertThat(result.getCourses()).isNotEmpty();
        assertThat(result.getCourses().iterator().next().getNumCourse()).isEqualTo(200L);
        verify(courseRepository, times(1)).findById(200L);
        verify(instructorRepository, times(1)).save(instructor);
    }

    @Test
    @DisplayName("Add Instructor and assign to Course - course not found")
    void addInstructorAndAssignToCourseNotFoundTest() {
        when(courseRepository.findById(999L)).thenReturn(Optional.empty());

        Instructor result = instructorServices.addInstructorAndAssignToCourse(instructor, 999L);

        assertThat(result).isNull();
        verify(courseRepository, times(1)).findById(999L);
        verify(instructorRepository, never()).save(any());
    }
}
