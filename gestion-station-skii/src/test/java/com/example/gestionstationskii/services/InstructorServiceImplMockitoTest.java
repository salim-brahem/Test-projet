package com.example.gestionstationskii.services;

import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.entities.Instructor;
import com.example.gestionstationskii.repositories.ICourseRepository;
import com.example.gestionstationskii.repositories.IInstructorRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class InstructorServiceImplMockitoTest {

    @Mock
    private IInstructorRepository instructorRepository;

    @Mock
    private ICourseRepository courseRepository;

    @InjectMocks
    private InstructorServicesImpl instructorService;

    @Test
    void testAddInstructor() {
        Instructor instructor = new Instructor(null, "Ali", "Ben Salah", LocalDate.now(), null);
        Instructor saved = new Instructor(1L, "Ali", "Ben Salah", LocalDate.now(), null);

        when(instructorRepository.save(instructor)).thenReturn(saved);

        Instructor result = instructorService.addInstructor(instructor);
        assertNotNull(result.getNumInstructor());
        verify(instructorRepository, times(1)).save(instructor);
    }

    @Test
    void testRetrieveAllInstructors() {
        when(instructorRepository.findAll()).thenReturn(Arrays.asList(
                new Instructor(1L, "Ali", "Ben Salah", LocalDate.now(), null),
                new Instructor(2L, "Mouna", "Trabelsi", LocalDate.now(), null)
        ));

        List<Instructor> instructors = instructorService.retrieveAllInstructors();
        assertEquals(2, instructors.size());
        verify(instructorRepository, times(1)).findAll();
    }

    @Test
    void testUpdateInstructor() {
        Instructor instructor = new Instructor(1L, "Ali", "Ben Salah", LocalDate.now(), null);
        when(instructorRepository.save(instructor)).thenReturn(instructor);

        Instructor updated = instructorService.updateInstructor(instructor);
        assertEquals("Ali", updated.getFirstName());
        verify(instructorRepository, times(1)).save(instructor);
    }

    @Test
    void testRetrieveInstructor() {
        Instructor instructor = new Instructor(1L, "Ali", "Ben Salah", LocalDate.now(), null);
        when(instructorRepository.findById(1L)).thenReturn(Optional.of(instructor));

        Instructor retrieved = instructorService.retrieveInstructor(1L);
        assertNotNull(retrieved);
        assertEquals("Ali", retrieved.getFirstName());
        verify(instructorRepository, times(1)).findById(1L);
    }

    @Test
    void testAddInstructorAndAssignToCourse() {
        Instructor instructor = new Instructor(null, "Rami", "Ben Youssef", LocalDate.now(), null);
        Course course = new Course();
        course.setNumCourse(5L);

        when(courseRepository.findById(5L)).thenReturn(Optional.of(course));
        when(instructorRepository.save(any(Instructor.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        Instructor saved = instructorService.addInstructorAndAssignToCourse(instructor, 5L);

        assertNotNull(saved.getCourses());
        assertTrue(saved.getCourses().contains(course));
        verify(courseRepository, times(1)).findById(5L);
        verify(instructorRepository, times(1)).save(instructor);
    }
}
