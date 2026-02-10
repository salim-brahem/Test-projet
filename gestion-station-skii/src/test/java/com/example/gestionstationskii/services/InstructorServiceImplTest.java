package com.example.gestionstationskii.services;

import com.example.gestionstationskii.entities.Instructor;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.junit.jupiter.api.extension.ExtendWith;

import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(SpringExtension.class)
@SpringBootTest
@Slf4j
public class InstructorServiceImplTest {

    @Autowired
    private IInstructorServices instructorService;

    @Test
    void testAddInstructor() {
        Instructor i = new Instructor();
        i.setFirstName("Ali");
        i.setLastName("Ben Salah");
        i.setDateOfHire(LocalDate.of(2020, 1, 10));

        Instructor saved = instructorService.addInstructor(i);

        assertNotNull(saved.getNumInstructor());
        assertEquals("Ali", saved.getFirstName());
        log.info("✅ Instructor added successfully: {}", saved);
    }

    @Test
    void testRetrieveAllInstructors() {
        List<Instructor> instructors = instructorService.retrieveAllInstructors();
        assertNotNull(instructors);
        assertTrue(instructors.size() >= 0);
        log.info("📘 Instructors retrieved: {}", instructors.size());
    }

    @Test
    void testUpdateInstructor() {
        Instructor i = new Instructor();
        i.setFirstName("Mouna");
        i.setLastName("Trabelsi");
        i.setDateOfHire(LocalDate.of(2021, 5, 15));

        Instructor saved = instructorService.addInstructor(i);
        saved.setLastName("Gharbi");

        Instructor updated = instructorService.updateInstructor(saved);
        assertEquals("Gharbi", updated.getLastName());
        log.info("✏️ Instructor updated successfully: {}", updated);
    }

    @Test
    void testRetrieveInstructor() {
        Instructor i = new Instructor();
        i.setFirstName("Sami");
        i.setLastName("Jlassi");
        i.setDateOfHire(LocalDate.of(2022, 3, 12));

        Instructor saved = instructorService.addInstructor(i);
        Instructor retrieved = instructorService.retrieveInstructor(saved.getNumInstructor());

        assertEquals(saved.getNumInstructor(), retrieved.getNumInstructor());
        log.info("🔍 Instructor retrieved successfully: {}", retrieved);
    }
}
