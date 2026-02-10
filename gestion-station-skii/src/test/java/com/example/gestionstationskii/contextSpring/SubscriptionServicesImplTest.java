package com.example.gestionstationskii.contextSpring;

import com.example.gestionstationskii.entities.Subscription;
import com.example.gestionstationskii.entities.TypeSubscription;
import com.example.gestionstationskii.repositories.ISkierRepository;
import com.example.gestionstationskii.repositories.ISubscriptionRepository;
import com.example.gestionstationskii.services.SubscriptionServicesImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.annotation.Rollback;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
@Rollback
class SubscriptionServicesImplTest {

    @Autowired
    private SubscriptionServicesImpl subscriptionServices;

    @Autowired
    private ISubscriptionRepository subscriptionRepository;

    @Autowired
    private ISkierRepository skierRepository;

    private Subscription monthlySub;
    private Subscription annualSub;

    @BeforeEach
    void setUp() {
        monthlySub = new Subscription();
        monthlySub.setStartDate(LocalDate.now());
        monthlySub.setPrice(100f);
        monthlySub.setTypeSub(TypeSubscription.MONTHLY);

        annualSub = new Subscription();
        annualSub.setStartDate(LocalDate.now());
        annualSub.setPrice(1000f);
        annualSub.setTypeSub(TypeSubscription.ANNUAL);
    }

    @Test
    void testAddSubscription_Monthly() {
        Subscription saved = subscriptionServices.addSubscription(monthlySub);
        assertNotNull(saved.getNumSub());
        assertEquals(monthlySub.getStartDate().plusMonths(1), saved.getEndDate());
    }

    @Test
    void testAddSubscription_Annual() {
        Subscription saved = subscriptionServices.addSubscription(annualSub);
        assertNotNull(saved.getNumSub());
        assertEquals(annualSub.getStartDate().plusYears(1), saved.getEndDate());
    }

    @Test
    void testRetrieveSubscriptionById() {
        Subscription saved = subscriptionServices.addSubscription(monthlySub);
        Subscription found = subscriptionServices.retrieveSubscriptionById(saved.getNumSub());
        assertNotNull(found);
        assertEquals(saved.getTypeSub(), found.getTypeSub());
    }

    @Test
    void testGetSubscriptionByType() {
        subscriptionServices.addSubscription(monthlySub);
        subscriptionServices.addSubscription(annualSub);
        Set<Subscription> monthlySubs = subscriptionServices.getSubscriptionByType(TypeSubscription.MONTHLY);
        assertFalse(monthlySubs.isEmpty());
        assertEquals(TypeSubscription.MONTHLY, monthlySubs.iterator().next().getTypeSub());
    }

    @Test
    void testRetrieveSubscriptionsByDates() {
        monthlySub.setStartDate(LocalDate.of(2025, 1, 1));
        annualSub.setStartDate(LocalDate.of(2025, 5, 1));

        subscriptionServices.addSubscription(monthlySub);
        subscriptionServices.addSubscription(annualSub);

        List<Subscription> result = subscriptionServices.retrieveSubscriptionsByDates(
                LocalDate.of(2025, 1, 1), LocalDate.of(2025, 12, 31));

        assertEquals(2, result.size());
    }
}
