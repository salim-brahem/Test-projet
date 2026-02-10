package com.example.gestionstationskii.mockito;
import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.entities.Support;
import com.example.gestionstationskii.entities.TypeCourse;
import com.example.gestionstationskii.repositories.ICourseRepository;
import com.example.gestionstationskii.services.CourseServicesImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class CourseServicesImplMockTest {

    @Mock
    private ICourseRepository courseRepository; // faux repository

    @InjectMocks
    private CourseServicesImpl courseServices;  // vrai service avec mocks injectés

    @Test
    void testAddCourse() {
        // GIVEN
        Course course = new Course();
        course.setNumCourse(1L);
        course.setLevel(2);
        course.setTypeCourse(TypeCourse.INDIVIDUAL);
        course.setSupport(Support.SKI);
        course.setPrice(150.0f);
        course.setTimeSlot(10);

        when(courseRepository.save(course)).thenReturn(course);

        // WHEN
        Course saved = courseServices.addCourse(course);

        // THEN
        assertNotNull(saved);
        assertEquals(TypeCourse.INDIVIDUAL, saved.getTypeCourse());
        verify(courseRepository, times(1)).save(course);
        System.out.println("✅ testAddCourse (Mockito) OK");
    }

    @Test
    void testRetrieveCourse() {
        // GIVEN
        Course course = new Course(1L, 2, TypeCourse.COLLECTIVE_ADULT, Support.SKI, 120.0f, 8, null);
        when(courseRepository.findById(1L)).thenReturn(Optional.of(course));

        // WHEN
        Course found = courseServices.retrieveCourse(1L);

        // THEN
        assertNotNull(found);
        assertEquals(2, found.getLevel());
        verify(courseRepository, times(1)).findById(1L);
        System.out.println("✅ testRetrieveCourse (Mockito) OK");
    }
}
