package com.example.gestionstationskii.contextSpring;
import com.example.gestionstationskii.entities.Course;
import com.example.gestionstationskii.entities.Support;
import com.example.gestionstationskii.entities.TypeCourse;
import com.example.gestionstationskii.repositories.ICourseRepository;
import com.example.gestionstationskii.services.CourseServicesImpl;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class CourseServicesImplTest {

    @Autowired
    private CourseServicesImpl courseServices; // ✅ vrai service, vrai contexte

    @Test
    void testAddAndRetrieveCourse() {
        // GIVEN
        Course course = new Course();
        course.setLevel(2);
        course.setTypeCourse(TypeCourse.INDIVIDUAL);
        course.setSupport(Support.SKI);
        course.setPrice(150.0f);
        course.setTimeSlot(10);

        // WHEN
        Course saved = courseServices.addCourse(course);
        Course retrieved = courseServices.retrieveCourse(saved.getNumCourse());

        // THEN
        assertNotNull(retrieved);
        assertEquals(saved.getNumCourse(), retrieved.getNumCourse());
        assertEquals(TypeCourse.INDIVIDUAL, retrieved.getTypeCourse());
        System.out.println("✅ testAddAndRetrieveCourse (Spring Context) OK");
    }

    @Test
    void testRetrieveAllCourses() {
        // WHEN
        List<Course> courses = courseServices.retrieveAllCourses();

        // THEN
        assertNotNull(courses);
        assertTrue(courses.size() >= 0);
        System.out.println("✅ testRetrieveAllCourses (Spring Context) OK");
    }
}
